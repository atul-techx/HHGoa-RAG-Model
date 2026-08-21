import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.dataset_loader import load_dataset, add_passage
from backend.chunking import ChunkingEngine
from backend.rag_engine import VectorRAGEngine
from backend.harness import ModelHarness, PipelineRequest, PipelineResponse
from backend.stt_service import SpeechToTextService
from backend.benchmark import LatencyBenchmarkSuite

app = FastAPI(
    title="Iris Voice-Enabled RAG API (#RAGInGoa)",
    description="Sub-200ms Iris Voice-Enabled RAG Pipeline with Engineered Chunking, Guardrails, Harness, & Latency Benchmarks.",
    version="1.0.0"
)

# CORS setup for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Engine & Harness Instances
rag_engine = VectorRAGEngine()
harness = ModelHarness(rag_engine)
benchmark_suite = LatencyBenchmarkSuite(harness)

class CompareRequest(BaseModel):
    query: str
    sample_text: Optional[str] = None

class DocumentRequest(BaseModel):
    title: str
    text: str
    category: str = "General"

@app.get("/api/health")
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "system": "Iris Voice RAG Pipeline (#RAGInGoa)",
        "indexed_chunks": len(rag_engine.indexed_chunks),
        "target_latency": "< 200ms"
    }

@app.get("/api/dataset")
@app.get("/dataset")
def get_dataset():
    passages = load_dataset()
    return {
        "total_documents": len(passages),
        "documents": passages,
        "current_strategy": rag_engine.current_strategy,
        "indexed_chunks": len(rag_engine.indexed_chunks)
    }

@app.post("/api/dataset/add")
@app.post("/dataset/add")
def add_document(doc: DocumentRequest):
    new_doc = add_passage(doc.title, doc.text, doc.category)
    # Re-index
    passages = load_dataset()
    rag_engine.index_documents(passages, strategy=rag_engine.current_strategy)
    return {"message": "Document added & vector store updated successfully.", "doc": new_doc}

@app.post("/api/query", response_model=PipelineResponse)
@app.post("/query", response_model=PipelineResponse)
def execute_rag_query(request: PipelineRequest):
    """Executes full Voice RAG pipeline inside structured harness."""
    try:
        return harness.execute_pipeline(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stt")
@app.post("/stt")
async def process_stt(
    provider: str = Form("sarvam"),
    api_key: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """Voice STT Endpoint for Sarvam AI / ElevenLabs audio file upload."""
    audio_bytes = await file.read()
    if provider == "sarvam":
        transcript, stt_ms = SpeechToTextService.transcribe_sarvam(audio_bytes, api_key=api_key)
    elif provider == "elevenlabs":
        transcript, stt_ms = SpeechToTextService.transcribe_elevenlabs(audio_bytes, api_key=api_key)
    else:
        transcript, stt_ms = "What is Retrieval Augmented Generation?", 25.0

    return {
        "transcript": transcript,
        "stt_provider": provider,
        "stt_latency_ms": stt_ms
    }

@app.post("/api/chunking/compare")
@app.post("/chunking/compare")
def compare_chunking(req: CompareRequest):
    """Compares the 5 engineered chunking strategies on a sample document or query."""
    doc = {
        "id": "sample_compare",
        "title": "RAG Chunking Benchmark Sample",
        "text": req.sample_text or (
            "Retrieval-Augmented Generation (RAG) improves Large Language Model accuracy by grounding responses "
            "in external documents. Naive fixed-size chunking splits documents rigidly by character length. "
            "Overlap-optimized chunking preserves context across boundaries. Semantic chunking splits text along "
            "sentence and paragraph breaks. Metadata-aware chunking injects document title and tags into chunks. "
            "Hierarchical chunking maps small child vectors back to parent context."
        ),
        "category": "RAG Engineering"
    }

    strategies = ["fixed_size", "overlap_optimized", "semantic", "metadata_aware", "hierarchical"]
    comparison = {}

    for strat in strategies:
        start_t = time.perf_counter()
        chunks = ChunkingEngine.process_document(doc, strategy=strat)
        # Test retrieval
        rag_engine.index_documents([doc], strategy=strat)
        retrieved, ret_ms = rag_engine.retrieve(req.query or "chunking strategies", top_k=2)
        proc_ms = (time.perf_counter() - start_t) * 1000

        comparison[strat] = {
            "chunk_count": len(chunks),
            "sample_chunk": chunks[0]["text"] if chunks else "",
            "retrieval_ms": ret_ms,
            "top_retrieval_score": retrieved[0]["score"] if retrieved else 0.0,
            "chunks_preview": chunks[:3]
        }

    # Reset index to dataset
    rag_engine.index_documents(load_dataset(), strategy="semantic")

    return {
        "query": req.query,
        "strategies": comparison
    }

@app.get("/api/benchmark")
@app.get("/benchmark")
def run_latency_benchmark(strategy: str = "semantic", num_queries: int = 25):
    """Runs automated latency benchmark across real test queries to compute P50, P70, P100."""
    return benchmark_suite.run_benchmark(chunking_strategy=strategy, num_queries=num_queries)
