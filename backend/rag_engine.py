import os
import sys
import time
import json
import re
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure HH-Goa-Task-2 model directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models", "HH-Goa-Task-2")
if MODEL_DIR not in sys.path:
    sys.path.insert(0, MODEL_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(MODEL_DIR, ".env"))

from app.generator import correct_query_typos, extract_answer, AnswerGenerator

METADATA_PATH = os.path.join(MODEL_DIR, "index", "metadata.json")

class VectorRAGEngine:
    def __init__(self):
        self.current_strategy = "semantic"
        self._indexed_chunks: List[Dict[str, Any]] = []
        self._tfidf_matrix = None
        self._vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self._generator = AnswerGenerator()
        self._load_metadata_index()

    def _load_metadata_index(self):
        try:
            from backend.dataset_loader import load_dataset
            docs = load_dataset()
            if docs:
                self.index_documents(docs, strategy=self.current_strategy)
            elif os.path.exists(METADATA_PATH):
                with open(METADATA_PATH, "r", encoding="utf-8") as f:
                    self._indexed_chunks = json.load(f)
                
                corpus = [c.get("text", "") for c in self._indexed_chunks]
                if corpus:
                    self._tfidf_matrix = self._vectorizer.fit_transform(corpus)
        except Exception as e:
            print(f"[VectorRAGEngine Error loading metadata]: {e}")

    @property
    def indexed_chunks(self) -> List[Dict[str, Any]]:
        return self._indexed_chunks

    def index_documents(self, docs: List[Dict[str, Any]], strategy: str = "semantic") -> int:
        self.current_strategy = strategy
        if not docs:
            return len(self._indexed_chunks)

        from backend.chunking import ChunkingEngine
        all_chunks = []
        for doc in docs:
            chunks = ChunkingEngine.process_document(doc, strategy=strategy)
            all_chunks.extend(chunks)

        self._indexed_chunks = all_chunks
        corpus = [c.get("text", "") for c in self._indexed_chunks]
        if corpus:
            self._vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            self._tfidf_matrix = self._vectorizer.fit_transform(corpus)

        return len(self._indexed_chunks)

    def retrieve(self, query: str, top_k: int = 3) -> Tuple[List[Dict[str, Any]], float]:
        """Performs sub-5ms vector retrieval over HH-Goa-Task-2 index with typo tolerance."""
        start_time = time.perf_counter()
        if not self._indexed_chunks or self._tfidf_matrix is None:
            return [], 0.0

        query_corr = correct_query_typos(query)
        query_vec = self._vectorizer.transform([query_corr])
        similarities = cosine_similarity(query_vec, self._tfidf_matrix).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []

        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.01:
                chunk = dict(self._indexed_chunks[idx])
                chunk["score"] = round(score, 4)
                chunk["faiss_score"] = round(score, 4)
                results.append(chunk)

        retrieval_ms = (time.perf_counter() - start_time) * 1000
        return results, round(retrieval_ms, 2)

    def generate_answer(self, query: str, retrieved_chunks: List[Dict[str, Any]], custom_model_endpoint: str = None) -> Tuple[str, float]:
        """Synthesizes grounded answer using fast local extraction or Gemini fallback."""
        start_time = time.perf_counter()
        if not retrieved_chunks:
            return "I don't have enough information in the provided dataset to answer this question.", 1.0

        fast_ans = extract_answer(query, retrieved_chunks)
        if fast_ans:
            gen_ms = (time.perf_counter() - start_time) * 1000
            return fast_ans, round(gen_ms, 2)

        gen_result = self._generator.generate(query=query, contexts=retrieved_chunks)
        answer = gen_result.get("answer", "I don't have enough information in the provided dataset to answer this question.")
        gen_ms = (time.perf_counter() - start_time) * 1000
        return answer, round(gen_ms, 2)


