import sys
import os
import json
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.pipeline import RAGPipeline

queries = [
    "what is a corporation?",
    "what is a company?",
    "what is artificial intelligence?",
    "what is a computer?",
    "what is machine learning?",
    "what is a database?",
    "what is the coporation"
]

if __name__ == "__main__":
    pipeline = RAGPipeline()

    print("\n" + "=" * 80)
    print("RUNNING FINAL RAG EVALUATION")
    print("=" * 80)

    results = []

    for q in queries:
        res = pipeline.run(q)
        results.append(res)

        print("\n" + "-" * 60)
        print(f"QUERY: {q}")
        print("-" * 60)
        print(f"Answer: {res['answer']}")
        print(f"Grounded: {res['grounded']}")
        print(f"Method: {res['method']}")
        lat = res['latency']
        print("Latency Breakdown:")
        print(f"  Retrieval  : {lat['retrieval_ms']} ms")
        print(f"  Reranking  : {lat['reranking_ms']} ms")
        print(f"  Answer     : {lat['answer_ms']} ms")
        print(f"  Guardrails : {lat['guardrails_ms']} ms")
        print(f"  Total RAG  : {lat['total_ms']} ms")

    out_file = os.path.join(PROJECT_ROOT, "final_eval_results.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        for res in results:
            f.write(f"\nQUERY: {res['query']}\n")
            f.write(f"Answer: {res['answer']}\n")
            f.write(f"Grounded: {res['grounded']}\n")
            f.write(f"Method: {res['method']}\n")
            lat = res['latency']
            f.write(f"Latency:\n")
            f.write(f"  Retrieval  : {lat['retrieval_ms']} ms\n")
            f.write(f"  Reranking  : {lat['reranking_ms']} ms\n")
            f.write(f"  Answer     : {lat['answer_ms']} ms\n")
            f.write(f"  Guardrails : {lat['guardrails_ms']} ms\n")
            f.write(f"  Total RAG  : {lat['total_ms']} ms\n")
