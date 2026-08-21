import time
import traceback
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.guardrails import GuardrailsEngine
from backend.rag_engine import VectorRAGEngine
from backend.dataset_loader import load_dataset

class PipelineRequest(BaseModel):
    query: str = Field(..., description="Transcribed voice query or text input")
    chunking_strategy: str = Field("semantic", description="Chunking strategy to use")
    top_k: int = Field(3, description="Number of vector chunks to retrieve")
    custom_model_endpoint: Optional[str] = Field(None, description="Optional custom LLM API endpoint")
    stt_provider: str = Field("web_speech", description="STT provider used (web_speech, sarvam, elevenlabs)")
    stt_latency_ms: float = Field(0.0, description="Latency spent in STT transcription")
    model_mode: str = Field("extractive_qa", description="Model engine mode (extractive_qa, generative_llm, hybrid_auto)")

class ExecutionTraceStep(BaseModel):
    step_name: str
    status: str # PASSED, FAILED, RETRIED, REJECTED
    duration_ms: float
    details: Dict[str, Any]

class PipelineResponse(BaseModel):
    query: str
    transcription_provider: str
    answer: str
    chunking_strategy: str
    retrieved_chunks: List[Dict[str, Any]]
    total_latency_ms: float
    latency_breakdown: Dict[str, float]
    guardrails_passed: bool
    guardrail_stage: str
    guardrail_reason: str
    grounding_score: float
    relevance_score: float
    retries_count: int
    trace: List[ExecutionTraceStep]
    hashtag: str = "#IrisAI"

class ModelHarness:
    def __init__(self, rag_engine: VectorRAGEngine):
        self.rag_engine = rag_engine
        self.dataset = load_dataset()
        # Initialize vector engine index
        self.rag_engine.index_documents(self.dataset, strategy="semantic")

    def execute_pipeline(self, request: PipelineRequest) -> PipelineResponse:
        """Runs full RAG pipeline inside a structured harness with error recovery and retries."""
        start_total = time.perf_counter()
        trace: List[ExecutionTraceStep] = []
        retries = 0

        # Step 0: STT Trace Recording
        trace.append(ExecutionTraceStep(
            step_name="Speech-to-Text Transcription",
            status="PASSED",
            duration_ms=request.stt_latency_ms,
            details={"provider": request.stt_provider, "query_text": request.query}
        ))

        # Re-index if strategy changed
        if self.rag_engine.current_strategy != request.chunking_strategy:
            t0 = time.perf_counter()
            self.rag_engine.index_documents(self.dataset, strategy=request.chunking_strategy)
            reindex_ms = (time.perf_counter() - t0) * 1000
            trace.append(ExecutionTraceStep(
                step_name="Dynamic Vector Re-Indexing",
                status="PASSED",
                duration_ms=round(reindex_ms, 2),
                details={"strategy": request.chunking_strategy, "total_chunks": len(self.rag_engine.indexed_chunks)}
            ))

        # Step 1: Pre-retrieval Guardrails Check
        t_g1_start = time.perf_counter()
        guardrail_eval = GuardrailsEngine.evaluate_query(request.query, self.dataset)
        g1_ms = (time.perf_counter() - t_g1_start) * 1000

        if not guardrail_eval["passed"]:
            trace.append(ExecutionTraceStep(
                step_name="Pre-Retrieval Guardrails",
                status="REJECTED",
                duration_ms=round(g1_ms, 2),
                details=guardrail_eval
            ))
            total_ms = (time.perf_counter() - start_total) * 1000
            return PipelineResponse(
                query=request.query,
                transcription_provider=request.stt_provider,
                answer=guardrail_eval["refusal_text"],
                chunking_strategy=request.chunking_strategy,
                retrieved_chunks=[],
                total_latency_ms=round(total_ms, 2),
                latency_breakdown={
                    "stt": request.stt_latency_ms,
                    "guardrails": round(g1_ms, 2),
                    "retrieval": 0.0,
                    "generation": 0.0
                },
                guardrails_passed=False,
                guardrail_stage=guardrail_eval["stage"],
                guardrail_reason=guardrail_eval["reason"],
                grounding_score=0.0,
                relevance_score=guardrail_eval.get("relevance_score", 0.0),
                retries_count=0,
                trace=trace
            )

        trace.append(ExecutionTraceStep(
            step_name="Pre-Retrieval Guardrails",
            status="PASSED",
            duration_ms=round(g1_ms, 2),
            details=guardrail_eval
        ))

        # Step 2: Vector Retrieval with Retry & Fallback Logic
        retrieved_chunks = []
        retrieval_ms = 0.0
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            t_ret_start = time.perf_counter()
            retrieved_chunks, ret_ms = self.rag_engine.retrieve(request.query, top_k=request.top_k)
            retrieval_ms += ret_ms

            # Harness Confidence Verification
            conf_passed, conf_reason = GuardrailsEngine.check_retrieval_confidence(retrieved_chunks)
            if conf_passed or attempt == max_retries:
                if not conf_passed and attempt > 0:
                    retries += 1
                break
            
            # Retry with relaxed query tokens
            retries += 1
            trace.append(ExecutionTraceStep(
                step_name=f"Vector Retrieval (Retry #{attempt+1})",
                status="RETRIED",
                duration_ms=round(ret_ms, 2),
                details={"reason": conf_reason, "attempt": attempt + 1}
            ))

        trace.append(ExecutionTraceStep(
            step_name="Vector DB Retrieval",
            status="PASSED" if retrieved_chunks else "EMPTY",
            duration_ms=round(retrieval_ms, 2),
            details={"retrieved_count": len(retrieved_chunks), "top_score": retrieved_chunks[0]["score"] if retrieved_chunks else 0.0}
        ))

        # Step 3: Answer Generation via Extractive Neural QA Transformer / Gemini LLM
        t_gen_start = time.perf_counter()
        raw_answer, gen_ms, model_telemetry = self.rag_engine.generate_answer(
            request.query, 
            retrieved_chunks, 
            custom_model_endpoint=request.custom_model_endpoint,
            model_mode=request.model_mode
        )
        
        trace.append(ExecutionTraceStep(
            step_name=f"Neural Model Answer Generation ({model_telemetry.get('model', 'distilbert-squad')})",
            status="PASSED",
            duration_ms=round(gen_ms, 2),
            details={
                "answer_length": len(raw_answer),
                "model_name": model_telemetry.get("model", "distilbert-squad"),
                "confidence_score": model_telemetry.get("confidence", 0.95),
                "mode": request.model_mode
            }
        ))

        # Step 4: Post-generation Grounding Guardrail Check
        t_g2_start = time.perf_counter()
        context_str = " ".join([c["text"] for c in retrieved_chunks])
        grounded, ground_msg, ground_score = GuardrailsEngine.check_answer_grounding(raw_answer, context_str)
        g2_ms = (time.perf_counter() - t_g2_start) * 1000

        final_answer = raw_answer
        guardrails_passed = True
        guardrail_stage = "passed"
        guardrail_reason = "All guardrails passed successfully."

        if not grounded:
            guardrails_passed = False
            guardrail_stage = "hallucination_prevention"
            guardrail_reason = ground_msg
            final_answer = "Refusing to answer: Generated statement failed hallucination/grounding validation check."
            trace.append(ExecutionTraceStep(
                step_name="Post-Generation Grounding Guardrail",
                status="REJECTED",
                duration_ms=round(g2_ms, 2),
                details={"grounding_score": ground_score, "reason": ground_msg}
            ))
        else:
            trace.append(ExecutionTraceStep(
                step_name="Post-Generation Grounding Guardrail",
                status="PASSED",
                duration_ms=round(g2_ms, 2),
                details={"grounding_score": ground_score}
            ))

        total_latency = (time.perf_counter() - start_total) * 1000

        return PipelineResponse(
            query=request.query,
            transcription_provider=request.stt_provider,
            answer=final_answer,
            chunking_strategy=request.chunking_strategy,
            retrieved_chunks=retrieved_chunks,
            total_latency_ms=round(total_latency, 2),
            latency_breakdown={
                "stt": round(request.stt_latency_ms, 2),
                "guardrails": round(g1_ms + g2_ms, 2),
                "retrieval": round(retrieval_ms, 2),
                "generation": round(gen_ms, 2)
            },
            guardrails_passed=guardrails_passed,
            guardrail_stage=guardrail_stage,
            guardrail_reason=guardrail_reason,
            grounding_score=round(ground_score, 3),
            relevance_score=guardrail_eval.get("relevance_score", 1.0),
            retries_count=retries,
            trace=trace
        )
