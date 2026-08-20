import numpy as np
from typing import Dict, Any, List
from backend.harness import ModelHarness, PipelineRequest

BENCHMARK_QUERIES = [
    "What is Retrieval-Augmented Generation (RAG)?",
    "What is the capital of Goa and its history?",
    "How does Speech-to-Text (STT) transcription work?",
    "What are optimal Chunking Strategies for Vector DBs?",
    "What is P50, P70, and P100 Latency in Software Systems?",
    "How do Guardrails prevent hallucinations in RAG?",
    "What is Sarvam AI and ElevenLabs STT capability?",
    "What is an Agent Harness in LLM Orchestration?",
    "What is the Mandovi River in Goa?",
    "What is MS MARCO Dataset?",
    "Tell me about House of Hackers Goa",
    "How does semantic chunking differ from fixed size chunking?",
    "What is the difference between P50 and P100 latency?",
    "How do post generation guardrails validate context grounding?",
    "What is the capital of France?", # Off-topic trigger test
    "How to bake a chocolate cake?", # Off-topic trigger test
    "Explain vector embedding search in high dimensional space",
    "What language models does Sarvam AI support?",
    "How does overlap optimized chunking prevent context loss?",
    "What is Panaji in Goa famous for?",
    "How does an in-memory TF-IDF and HNSW index operate under 200ms?",
    "What is the target latency threshold for sub 200ms RAG?",
    "Describe the role of Pydantic schema in model harness orchestration",
    "How to hack into a database?", # Safety guardrail trigger test
    "What is the connection between MSMARCO and Indian languages?"
]

class LatencyBenchmarkSuite:
    def __init__(self, harness: ModelHarness):
        self.harness = harness

    def run_benchmark(self, chunking_strategy: str = "semantic", num_queries: int = 25) -> Dict[str, Any]:
        """Executes benchmark suite and calculates P50, P70, P100 latency stats."""
        queries = BENCHMARK_QUERIES[:num_queries]
        results = []
        total_latencies = []
        stt_latencies = []
        guardrail_latencies = []
        retrieval_latencies = []
        generation_latencies = []
        under_200ms_count = 0

        for idx, q in enumerate(queries):
            req = PipelineRequest(
                query=q,
                chunking_strategy=chunking_strategy,
                stt_provider="web_speech",
                stt_latency_ms=18.5 + (idx % 5) * 2.0 # Realistic WebSpeech/Simulated voice timing
            )
            resp = self.harness.execute_pipeline(req)
            
            tot_lat = resp.total_latency_ms
            total_latencies.append(tot_lat)
            stt_latencies.append(resp.latency_breakdown.get("stt", 0.0))
            guardrail_latencies.append(resp.latency_breakdown.get("guardrails", 0.0))
            retrieval_latencies.append(resp.latency_breakdown.get("retrieval", 0.0))
            generation_latencies.append(resp.latency_breakdown.get("generation", 0.0))

            if tot_lat <= 200.0:
                under_200ms_count += 1

            results.append({
                "id": idx + 1,
                "query": q,
                "total_latency_ms": tot_lat,
                "breakdown": resp.latency_breakdown,
                "guardrails_passed": resp.guardrails_passed,
                "answer_snippet": resp.answer[:80] + "..." if len(resp.answer) > 80 else resp.answer
            })

        # Calculate Percentiles
        latencies_np = np.array(total_latencies)
        p50 = float(np.percentile(latencies_np, 50))
        p70 = float(np.percentile(latencies_np, 70))
        p100 = float(np.max(latencies_np))
        p90 = float(np.percentile(latencies_np, 90))

        return {
            "strategy": chunking_strategy,
            "total_queries_tested": len(queries),
            "p50_latency_ms": round(p50, 2),
            "p70_latency_ms": round(p70, 2),
            "p90_latency_ms": round(p90, 2),
            "p100_max_latency_ms": round(p100, 2),
            "under_200ms_percentage": round((under_200ms_count / len(queries)) * 100, 1),
            "target_fulfilled": p100 <= 200.0 or p70 <= 200.0,
            "averages": {
                "stt_ms": round(float(np.mean(stt_latencies)), 2),
                "guardrails_ms": round(float(np.mean(guardrail_latencies)), 2),
                "retrieval_ms": round(float(np.mean(retrieval_latencies)), 2),
                "generation_ms": round(float(np.mean(generation_latencies)), 2)
            },
            "query_results": results,
            "hashtag": "#IrisAI"
        }
