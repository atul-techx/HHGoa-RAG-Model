import sys
import os
import json
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.pipeline import RAGPipeline

queries = [
    "what is the corporation?",
    "what is the coporation?",
    "what is a company?",
    "what is artificial intelligence?",
    "what is a computer?",
    "what is machine learning?",
    "what is a database?"
]

if __name__ == "__main__":
    pipeline = RAGPipeline()

    results = []

    for q in queries:
        res = pipeline.run(q)
        results.append(res)

    out_file = os.path.join(PROJECT_ROOT, "user_eval_results.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        for res in results:
            f.write(f"\n------------------------------------------------------------\n")
            f.write(f"QUERY: {res['query']}\n")
            f.write(f"------------------------------------------------------------\n")
            f.write(f"Answer: {res['answer']}\n")
            f.write(f"Grounded: {res['grounded']}\n")
            f.write(f"Method: {res['method']}\n")
            lat = res['latency']
            f.write(f"Latency Breakdown:\n")
            f.write(f"  Retrieval  : {lat['retrieval_ms']} ms\n")
            f.write(f"  Reranking  : {lat['reranking_ms']} ms\n")
            f.write(f"  Answer     : {lat['answer_ms']} ms\n")
            f.write(f"  Guardrails : {lat['guardrails_ms']} ms\n")
            f.write(f"  Total RAG  : {lat['total_ms']} ms\n")

    print("Wrote user_eval_results.txt")
