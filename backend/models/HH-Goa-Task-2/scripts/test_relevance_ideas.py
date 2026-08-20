import sys
import os
import json
import re

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

out_file = os.path.join(PROJECT_ROOT, "relevance_out.txt")
with open(out_file, "w", encoding="utf-8") as f:
    pipeline = RAGPipeline()
    for q in queries:
        f.write(f"\n=======================================================\n")
        f.write(f"QUERY: '{q}'\n")
        f.write(f"=======================================================\n")
        docs = pipeline.retrieve(q, top_k=3)
        for i, doc in enumerate(docs):
            f.write(f"\n  Doc [{i}] Score: {doc.get('faiss_score', 0):.4f}\n")
            text = doc.get("text", "")
            f.write(f"  Full Text: {text}\n")

print("Wrote relevance_out.txt")
