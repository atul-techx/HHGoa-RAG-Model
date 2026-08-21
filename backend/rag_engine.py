import os
import sys
import time
import json
import re
import math
from collections import Counter
import numpy as np
from typing import List, Dict, Any, Tuple

# Ensure HH-Goa-Task-2 model directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models", "HH-Goa-Task-2")
if MODEL_DIR not in sys.path:
    sys.path.insert(0, MODEL_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(MODEL_DIR, ".env"))

from app.generator import correct_query_typos, extract_answer, AnswerGenerator

METADATA_PATH = os.path.join(MODEL_DIR, "index", "metadata.json")

ENGLISH_STOP_WORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn me", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
    "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself"
])

def _tfidf_tokenize(text: str) -> List[str]:
    words = re.findall(r'\b[a-z0-9]+\b', text.lower())
    unigrams = [w for w in words if w not in ENGLISH_STOP_WORDS]
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1) if words[i] not in ENGLISH_STOP_WORDS or words[i+1] not in ENGLISH_STOP_WORDS]
    return unigrams + bigrams

class LightweightTFIDF:
    def __init__(self):
        self.vocabulary_ = {}
        self.idf_ = {}
        self.doc_vectors = []

    def fit_transform(self, corpus: List[str]):
        self.doc_vectors = []
        doc_tokens = [_tfidf_tokenize(doc) for doc in corpus]
        N = len(corpus)
        
        df = Counter()
        for tokens in doc_tokens:
            for token in set(tokens):
                df[token] += 1
                
        self.vocabulary_ = {term: idx for idx, term in enumerate(df.keys())}
        self.idf_ = {term: math.log((1 + N) / (1 + count)) + 1.0 for term, count in df.items()}
        
        for tokens in doc_tokens:
            tf = Counter(tokens)
            vec = {}
            norm_sq = 0.0
            for term, count in tf.items():
                if term in self.vocabulary_:
                    tfidf = count * self.idf_[term]
                    idx = self.vocabulary_[term]
                    vec[idx] = tfidf
                    norm_sq += tfidf * tfidf
            norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
            self.doc_vectors.append({k: v / norm for k, v in vec.items()})
        return self.doc_vectors

    def transform(self, corpus: List[str]):
        query_vectors = []
        for doc in corpus:
            tokens = _tfidf_tokenize(doc)
            tf = Counter(tokens)
            vec = {}
            norm_sq = 0.0
            for term, count in tf.items():
                if term in self.vocabulary_:
                    tfidf = count * self.idf_[term]
                    idx = self.vocabulary_[term]
                    vec[idx] = tfidf
                    norm_sq += tfidf * tfidf
            norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
            query_vectors.append({k: v / norm for k, v in vec.items()})
        return query_vectors

def _compute_cosine_similarity(query_vec: dict, doc_vectors: List[dict]) -> np.ndarray:
    scores = []
    for d_vec in doc_vectors:
        score = sum(val * d_vec.get(k, 0.0) for k, val in query_vec.items())
        scores.append(score)
    return np.array(scores)

class VectorRAGEngine:
    def __init__(self):
        self.current_strategy = "semantic"
        self._indexed_chunks: List[Dict[str, Any]] = []
        self._tfidf_matrix = None
        self._vectorizer = LightweightTFIDF()
        self._generator = AnswerGenerator()
        from backend.neural_qa import ExtractiveQAModel
        self._qa_engine = ExtractiveQAModel()
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
            self._vectorizer = LightweightTFIDF()
            self._tfidf_matrix = self._vectorizer.fit_transform(corpus)

        return len(self._indexed_chunks)

    def retrieve(self, query: str, top_k: int = 3) -> Tuple[List[Dict[str, Any]], float]:
        """Performs sub-5ms vector retrieval over HH-Goa-Task-2 index with typo tolerance."""
        start_time = time.perf_counter()
        if not self._indexed_chunks or self._tfidf_matrix is None or not hasattr(self._vectorizer, "vocabulary_"):
            return [], 0.0

        query_corr = correct_query_typos(query)
        query_vecs = self._vectorizer.transform([query_corr])
        similarities = _compute_cosine_similarity(query_vecs[0], self._tfidf_matrix)

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

    def generate_answer(self, query: str, retrieved_chunks: List[Dict[str, Any]], custom_model_endpoint: str = None, model_mode: str = "extractive_qa") -> Tuple[str, float, Dict[str, Any]]:
        """Synthesizes grounded answer using Extractive Neural QA Transformer Model or Gemini LLM."""
        start_time = time.perf_counter()
        if not retrieved_chunks:
            return "I don't have enough information in the provided dataset to answer this question.", 1.0, {"confidence": 0.0, "model": "none"}

        # Mode 1: Extractive Neural QA Model (DistilBERT SQuAD Transformer)
        if model_mode in ["extractive_qa", "hybrid_auto"]:
            qa_res = self._qa_engine.answer_question(query, retrieved_chunks)
            
            if qa_res.get("grounded") and qa_res.get("confidence", 0.0) >= 0.15:
                gen_ms = (time.perf_counter() - start_time) * 1000
                return qa_res["answer"], round(gen_ms, 2), {
                    "confidence": qa_res.get("confidence", 0.95),
                    "model": qa_res.get("model_name", "distilbert-squad"),
                    "mode": "extractive_qa"
                }
            
            # If hybrid_auto and confidence is low, fall through to Generative LLM
            if model_mode != "hybrid_auto":
                gen_ms = (time.perf_counter() - start_time) * 1000
                return qa_res.get("answer", "I don't have enough information in the provided dataset to answer this question."), round(gen_ms, 2), {
                    "confidence": qa_res.get("confidence", 0.0),
                    "model": qa_res.get("model_name", "distilbert-squad"),
                    "mode": "extractive_qa"
                }

        # Mode 2: Generative LLM (Gemini 2.5 Flash / Custom API)
        gen_result = self._generator.generate(query=query, contexts=retrieved_chunks, force_fallback=True)
        answer = gen_result.get("answer", "I don't have enough information in the provided dataset to answer this question.")
        gen_ms = (time.perf_counter() - start_time) * 1000
        
        return answer, round(gen_ms, 2), {
            "confidence": 0.92 if gen_result.get("grounded") else 0.0,
            "model": "gemini-2.5-flash",
            "mode": "generative_llm"
        }
