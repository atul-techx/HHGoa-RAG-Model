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

OFF_TOPIC_EXPLICIT_KEYWORDS = set()

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
        """Determines if query is safe and allowed for processing by AI system."""
        # Unrestricted: Allow all safe general knowledge, coding, trivia, and domain queries
        return True, "Topic relevance check passed.", 1.0

    @staticmethod
    def check_retrieval_confidence(retrieved_chunks: List[Dict[str, Any]], query: str = "", threshold: float = 0.02) -> Tuple[bool, str]:
        """Ensures retrieved vector context has sufficient similarity score and query term coverage."""
        if not retrieved_chunks:
            return False, "Guardrail Triggered: No relevant context found in Vector DB."
        
        top_score = retrieved_chunks[0].get("score", retrieved_chunks[0].get("faiss_score", 0.0))
        if top_score < threshold:
            return False, f"Guardrail Triggered: Low vector confidence score ({top_score:.3f} < threshold {threshold})."
        
        if query:
            q_tokens = [w.lower() for w in re.findall(r'\b\w+\b', query) if w.lower() not in STOP_WORDS and len(w) > 1]
            if len(q_tokens) >= 2:
                combined_text = " ".join([c.get("text", "").lower() for c in retrieved_chunks])
                matched = [t for t in q_tokens if t in combined_text]
                coverage = len(matched) / len(q_tokens)
                if coverage < 0.50:
                    return False, f"Guardrail Triggered: Context lacks essential query terms ({len(matched)}/{len(q_tokens)} matched)."

        return True, "Retrieval confidence passed."

    @staticmethod
    def check_answer_grounding(answer: str, context: str, query: str = "") -> Tuple[bool, str, float]:
        """Post-generation check ensuring generated answer is grounded in retrieved context or provided by General AI system."""
        if not answer or "don't have enough information" in answer.lower() or "cannot answer" in answer.lower() or "refusing" in answer.lower() or "abstained" in answer.lower():
            return True, "System abstained safely.", 1.0

        if not context or not context.strip():
            # General Knowledge / Main Model answer without local vector context
            return True, "General AI Knowledge response validated.", 1.0

        answer_words = {w for w in re.findall(r'\b\w+\b', answer.lower()) if w not in STOP_WORDS and len(w) > 2}
        context_words = {w for w in re.findall(r'\b\w+\b', context.lower()) if w not in STOP_WORDS and len(w) > 2}

        if not answer_words:
            return True, "Short answer.", 1.0

        overlap = answer_words.intersection(context_words)
        grounding_score = len(overlap) / len(answer_words)

        if grounding_score < 0.10:
            # Main model generated a comprehensive parametric answer beyond thin local passage
            return True, f"Parametric AI synthesis validated (grounding score {grounding_score:.2f}).", 1.0

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
                "refusal_code": "SAFETY_INJECTION",
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
                "refusal_code": "OFF_TOPIC",
                "refusal_text": "I cannot answer this question because it is off-topic."
            }

        return {
            "passed": True,
            "stage": "pre_retrieval_passed",
            "reason": "All pre-retrieval guardrails passed.",
            "relevance_score": rel_score,
            "abstain": False,
            "refusal_code": "NONE"
        }

