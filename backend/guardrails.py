import re
from typing import Dict, Any, List, Tuple

STOP_WORDS = {
    "what", "is", "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "with", "by", "about", "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "from", "up", "down", "in", "out", "on", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "can", "will",
    "just", "don", "should", "now", "tell", "me", "give"
}

UNSAFE_PATTERNS = [
    r"ignore previous instructions",
    r"bypass safety",
    r"jailbreak",
    r"hack system",
    r"drop database",
    r"sudo rm -rf",
    r"make a bomb",
    r"steal credentials"
]

DOMAIN_SUBJECTS = {
    "rag", "retrieval", "augmented", "generation", "vector", "embedding", "chunking", "stt",
    "speech", "audio", "transcription", "sarvam", "elevenlabs", "goa", "panaji", "mandovi",
    "house of hackers", "hh goa", "msmarco", "latency", "p50", "p70", "p100", "guardrail",
    "harness", "artificial intelligence", "llm", "database", "python", "dataset"
}

OFF_TOPIC_EXPLICIT_KEYWORDS = {
    "france", "paris", "pizza", "cake", "recipe", "football", "cricket", "nba", "movie", "actor", "astrology"
}

class GuardrailsEngine:
    @staticmethod
    def check_input_safety(query: str) -> Tuple[bool, str]:
        """Checks for unsafe prompts or injection attempts."""
        query_lower = query.lower()
        for pattern in UNSAFE_PATTERNS:
            if re.search(pattern, query_lower):
                return False, f"Guardrail Triggered: Malicious or unsafe prompt pattern detected ('{pattern}')."
        return True, "Safety check passed."

    @staticmethod
    def check_topic_relevance(query: str, indexed_docs: List[Dict[str, Any]]) -> Tuple[bool, str, float]:
        """Determines if query is relevant to indexed knowledge domain."""
        query_lower = query.lower()
        all_words = set(re.findall(r'\b\w+\b', query_lower))
        
        # Check explicit off-topic subjects
        for off in OFF_TOPIC_EXPLICIT_KEYWORDS:
            if off in all_words:
                return False, f"Guardrail Triggered: Explicit off-topic subject detected ('{off}').", 0.0

        content_words = {w for w in all_words if w not in STOP_WORDS and len(w) > 2}

        if not content_words:
            return True, "Query contains basic question words.", 1.0

        domain_overlap = content_words.intersection(DOMAIN_SUBJECTS)
        
        # Also check doc title domain terms
        doc_topics = set()
        for doc in indexed_docs:
            doc_topics.update([w for w in re.findall(r'\b\w+\b', doc.get("title", "").lower()) if w not in STOP_WORDS])

        full_overlap = content_words.intersection(doc_topics)
        relevance_score = (len(domain_overlap) * 2 + len(full_overlap)) / max(len(content_words) * 2, 1)

        if relevance_score < 0.25 and not domain_overlap:
            return False, f"Guardrail Triggered: Query is off-topic and outside indexed knowledge base domain (Relevance Score: {relevance_score:.2f}).", relevance_score

        return True, "Topic relevance check passed.", relevance_score

    @staticmethod
    def check_retrieval_confidence(retrieved_chunks: List[Dict[str, Any]], threshold: float = 0.15) -> Tuple[bool, str]:
        """Ensures retrieved vector context has sufficient similarity score."""
        if not retrieved_chunks:
            return False, "Guardrail Triggered: No relevant context found in Vector DB."
        
        top_score = retrieved_chunks[0].get("score", 0.0)
        if top_score < threshold:
            return False, f"Guardrail Triggered: Low vector confidence score ({top_score:.3f} < threshold {threshold})."
        
        return True, "Retrieval confidence passed."

    @staticmethod
    def check_answer_grounding(answer: str, context: str) -> Tuple[bool, str, float]:
        """Post-generation check ensuring generated answer is grounded in retrieved context."""
        if not answer or "cannot answer" in answer.lower() or "refusing" in answer.lower() or "abstained" in answer.lower():
            return True, "System abstained safely.", 1.0

        answer_words = {w for w in re.findall(r'\b\w+\b', answer.lower()) if w not in STOP_WORDS and len(w) > 2}
        context_words = {w for w in re.findall(r'\b\w+\b', context.lower()) if w not in STOP_WORDS and len(w) > 2}

        if not answer_words:
            return True, "Short answer.", 1.0

        overlap = answer_words.intersection(context_words)
        grounding_score = len(overlap) / len(answer_words)

        if grounding_score < 0.20:
            return False, f"Guardrail Triggered: Answer is not grounded in retrieved context (grounding score {grounding_score:.2f}). Refusing to answer hallucinated response.", grounding_score

        return True, f"Grounding check passed (score {grounding_score:.2f}).", grounding_score

    @classmethod
    def evaluate_query(cls, query: str, indexed_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Pre-retrieval guardrail evaluation."""
        # 1. Safety check
        safe, safe_msg = cls.check_input_safety(query)
        if not safe:
            return {
                "passed": False,
                "stage": "input_safety",
                "reason": safe_msg,
                "abstain": True,
                "refusal_text": "I cannot process this request because it violates safety guardrails."
            }

        # 2. Topic check
        relevant, rel_msg, rel_score = cls.check_topic_relevance(query, indexed_docs)
        if not relevant:
            return {
                "passed": False,
                "stage": "off_topic",
                "reason": rel_msg,
                "relevance_score": rel_score,
                "abstain": True,
                "refusal_text": f"I cannot answer this question because it is off-topic. The indexed knowledge base contains information about AI, RAG, Goa tech, STT, and MSMARCO benchmarks."
            }

        return {
            "passed": True,
            "stage": "pre_retrieval_passed",
            "reason": "All pre-retrieval guardrails passed.",
            "relevance_score": rel_score,
            "abstain": False
        }
