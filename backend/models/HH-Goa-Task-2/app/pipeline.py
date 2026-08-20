import os
import sys
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


import torch
import faiss
from sentence_transformers import SentenceTransformer

from app.reranker import Reranker
from app.generator import AnswerGenerator, NO_ANSWER, correct_query_typos
from app.guardrails import Guardrails
# PROJECT PATHS

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

INDEX_DIR = os.path.join(
    PROJECT_ROOT,
    "index"
)

FAISS_INDEX_PATH = os.path.join(
    INDEX_DIR,
    "rag.index"
)

METADATA_PATH = os.path.join(
    INDEX_DIR,
    "metadata.json"
)

# CONFIGURATIO

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

RETRIEVAL_TOP_K = 3

RERANK_ENABLED = False
RERANK_TOP_K = 0


# Set PyTorch thread count for optimal CPU inference
if torch.cuda.is_available():
    pass
else:
    torch.set_num_threads(max(1, os.cpu_count() // 2 if os.cpu_count() else 4))


# ============================================================
# RAG PIPELINE
# ============================================================

class RAGPipeline:

    def __init__(self):

        print("=" * 70)
        print("INITIALIZING RAG PIPELINE (FAST CPU PATH)")
        print("=" * 70)

        # ----------------------------------------------------
        # Load FAISS Index
        # ----------------------------------------------------
        print("\nLoading FAISS index...")
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        print(f"FAISS index loaded: {self.index.ntotal} vectors")

        # ----------------------------------------------------
        # Load Metadata
        # ----------------------------------------------------
        print("\nLoading metadata...")
        with open(METADATA_PATH, "r", encoding="utf-8") as file:
            self.metadata = json.load(file)
        print(f"Metadata loaded: {len(self.metadata)} entries")

        # ----------------------------------------------------
        # Load Embedding Model & Warm Up
        # ----------------------------------------------------
        print("\nLoading embedding model...")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.embedding_model.eval()

        print("Warming up embedding model...")
        with torch.no_grad():
            _ = self.embedding_model.encode(
                ["warmup query"],
                normalize_embeddings=True,
                batch_size=1
            )
        print("Embedding model warmed up.")

        # ----------------------------------------------------
        # Guardrails
        # ----------------------------------------------------
        self.guardrails = Guardrails()

        # ----------------------------------------------------
        # Reranker (Lazy loaded if RERANK_ENABLED)
        # ----------------------------------------------------
        self.reranker = Reranker() if RERANK_ENABLED else None

        # ----------------------------------------------------
        # Generator
        # ----------------------------------------------------
        self.generator = AnswerGenerator()

        print("\nRAG pipeline initialized and ready.")

    # ========================================================
    # RETRIEVAL
    # ========================================================

    def retrieve(self, query, top_k=RETRIEVAL_TOP_K):
        query_corr = correct_query_typos(query)
        with torch.no_grad():
            query_embedding = self.embedding_model.encode(
                [query_corr],
                normalize_embeddings=True,
                batch_size=1
            )

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        documents = []
        for score, index_id in zip(scores[0], indices[0]):
            if index_id < 0 or index_id >= len(self.metadata):
                continue

            document = self.metadata[index_id].copy()
            document["faiss_score"] = float(score)
            documents.append(document)

        return documents

    # ========================================================
    # COMPLETE RAG PIPELINE
    # ========================================================

    def run(self, query):
        total_start = time.perf_counter()

        query_str = (query or "").strip()

        # ----------------------------------------------------
        # 1. Guardrails: Query Validation
        # ----------------------------------------------------
        guardrail_start = time.perf_counter()
        query_check = self.guardrails.validate_query(query_str)
        guardrail_query_time = (time.perf_counter() - guardrail_start) * 1000

        if not query_check["allowed"]:
            total_latency = (time.perf_counter() - total_start) * 1000
            return {
                "query": query_str,
                "answer": "Please provide a valid question.",
                "grounded": False,
                "method": "guardrail_rejected",
                "retrieved": [],
                "reranked": [],
                "latency": {
                    "retrieval_ms": 0.0,
                    "reranking_ms": 0.0,
                    "answer_ms": 0.0,
                    "generation_ms": 0.0,
                    "guardrails_ms": round(guardrail_query_time, 2),
                    "total_ms": round(total_latency, 2)
                }
            }

        # ----------------------------------------------------
        # 2. Retrieval
        # ----------------------------------------------------
        retrieval_start = time.perf_counter()
        documents = self.retrieve(query_str, top_k=RETRIEVAL_TOP_K)
        retrieval_latency = (time.perf_counter() - retrieval_start) * 1000

        # ----------------------------------------------------
        # 3. Guardrails: Retrieval Check
        # ----------------------------------------------------
        g_ret_start = time.perf_counter()
        retrieval_check = self.guardrails.validate_retrieval(documents)
        guardrail_ret_time = (time.perf_counter() - g_ret_start) * 1000

        if not retrieval_check["grounded"]:
            total_latency = (time.perf_counter() - total_start) * 1000
            guardrails_total = guardrail_query_time + guardrail_ret_time
            return {
                "query": query_str,
                "answer": NO_ANSWER,
                "grounded": False,
                "method": "insufficient_context",
                "retrieved": documents,
                "reranked": documents,
                "latency": {
                    "retrieval_ms": round(retrieval_latency, 2),
                    "reranking_ms": 0.0,
                    "answer_ms": 0.0,
                    "generation_ms": 0.0,
                    "guardrails_ms": round(guardrails_total, 2),
                    "total_ms": round(total_latency, 2)
                }
            }

        # ----------------------------------------------------
        # 4. Reranking (Optional)
        # ----------------------------------------------------
        rerank_start = time.perf_counter()
        if RERANK_ENABLED and self.reranker:
            reranked_documents = self.reranker.rerank(
                query=query_str,
                documents=documents,
                top_k=RERANK_TOP_K if RERANK_TOP_K > 0 else RETRIEVAL_TOP_K
            )
        else:
            reranked_documents = documents
        rerank_latency = (time.perf_counter() - rerank_start) * 1000

        # ----------------------------------------------------
        # 5. Answer Generation (Fast Local Path / Gemini Fallback)
        # ----------------------------------------------------
        answer_start = time.perf_counter()
        gen_result = self.generator.generate(
            query=query_str,
            contexts=reranked_documents
        )
        answer_latency = (time.perf_counter() - answer_start) * 1000

        raw_answer = gen_result.get("answer", NO_ANSWER)
        method = gen_result.get("method", "local_context_answer")
        grounded = gen_result.get("grounded", False)

        # 6. Guardrails: Answer Validation
        g_ans_start = time.perf_counter()
        if grounded and raw_answer != NO_ANSWER:
            answer_check = self.guardrails.validate_answer(raw_answer, reranked_documents)
            if not answer_check["grounded"]:
                raw_answer = NO_ANSWER
                grounded = False
                method = "ungrounded_answer_rejected"
        guardrail_ans_time = (time.perf_counter() - g_ans_start) * 1000

        guardrails_total = (
            guardrail_query_time + guardrail_ret_time + guardrail_ans_time
        )
        total_latency = (time.perf_counter() - total_start) * 1000

        return {
            "query": query_str,
            "answer": raw_answer,
            "grounded": grounded,
            "method": method,
            "retrieved": documents,
            "reranked": reranked_documents,
            "latency": {
                "retrieval_ms": round(retrieval_latency, 2),
                "reranking_ms": round(rerank_latency, 2),
                "answer_ms": round(answer_latency, 2),
                "generation_ms": round(answer_latency, 2),
                "guardrails_ms": round(guardrails_total, 2),
                "total_ms": round(total_latency, 2)
            }
        }


# ============================================================
# INTERACTIVE TEST
# ============================================================

if __name__ == "__main__":

    pipeline = RAGPipeline()

    print()
    print("=" * 70)
    print("END-TO-END RAG READY")
    print("=" * 70)

    print("\nType a question. Type 'exit' to stop.")

    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() == "exit":
            print("\nExiting...")
            break
        if not question:
            continue

        result = pipeline.run(question)

        print("\n" + "=" * 70)
        print("FINAL ANSWER")
        print("=" * 70)
        print(result["answer"])

        print(f"\nGrounded: {result['grounded']}")
        print(f"Method: {result['method']}")

        latency = result["latency"]
        print("\nLatency Breakdown:")
        print(f"Retrieval  : {latency['retrieval_ms']} ms")
        print(f"Reranking  : {latency['reranking_ms']} ms")
        print(f"Answer     : {latency['answer_ms']} ms")
        print(f"Guardrails : {latency['guardrails_ms']} ms")
        print(f"Total RAG  : {latency['total_ms']} ms")