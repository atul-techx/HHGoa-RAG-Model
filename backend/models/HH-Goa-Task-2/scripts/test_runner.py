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
    "what is a database?"
]

if __name__ == "__main__":
    out_file = os.path.join(PROJECT_ROOT, "test_out.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        pipeline = RAGPipeline()
        for q in queries:
            f.write(f"\n--- QUERY: {q} ---\n")
            res = pipeline.run(q)
            f.write(f"Answer: {res['answer']}\n")
            f.write(f"Grounded: {res['grounded']}\n")
            f.write(f"Method: {res['method']}\n")
            f.write(f"Latency: {res['latency']}\n")
            f.write("Retrieved texts:\n")
            for i, doc in enumerate(res['retrieved']):
                f.write(f"  [{i}] Score: {doc.get('faiss_score', 0):.4f} | Text: {doc.get('text', '')[:150]}\n")
    print("Done writing test_out.txt")
