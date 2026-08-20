import sys
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.pipeline import RAGPipeline

p = RAGPipeline()
docs = p.retrieve("what is the coporation", top_k=10)

out_file = os.path.join(PROJECT_ROOT, "coporation_docs.txt")
with open(out_file, "w", encoding="utf-8") as f:
    f.write("Retrieved docs for 'what is the coporation':\n\n")
    for i, d in enumerate(docs):
        f.write(f"Doc [{i}] Score: {d.get('faiss_score', 0):.4f}\n")
        f.write(f"Text: {d.get('text', '')}\n\n")

print("Saved coporation_docs.txt")
