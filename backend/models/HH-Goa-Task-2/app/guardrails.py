import re


class Guardrails:

    def __init__(
        self,
        minimum_score=0.25,
        minimum_context_length=15
    ):
        self.minimum_score = minimum_score
        self.minimum_context_length = minimum_context_length

    def validate_query(self, query):
        if not query:
            return {
                "allowed": False,
                "reason": "empty_query"
            }

        query = query.strip()

        if len(query) < 2:
            return {
                "allowed": False,
                "reason": "query_too_short"
            }

        suspicious_patterns = [
            r"ignore previous instructions",
            r"ignore all instructions",
            r"system prompt",
            r"reveal your prompt",
            r"developer message",
            r"jailbreak",
            r"bypass your rules"
        ]

        query_lower = query.lower()

        for pattern in suspicious_patterns:
            if re.search(pattern, query_lower):
                return {
                    "allowed": False,
                    "reason": "prompt_injection"
                }

        return {
            "allowed": True,
            "reason": "valid"
        }

    def validate_retrieval(self, documents):
        if not documents:
            return {
                "grounded": False,
                "reason": "no_retrieved_context"
            }

        top_score = documents[0].get("faiss_score", 0.0) if documents else 0.0
        if top_score < self.minimum_score:
            return {
                "grounded": False,
                "reason": "low_similarity_score"
            }

        valid_documents = []
        for document in documents:
            text = document.get("text", "")
            if not text:
                continue

            if len(text.strip()) < self.minimum_context_length:
                continue

            valid_documents.append(document)

        if not valid_documents:
            return {
                "grounded": False,
                "reason": "insufficient_context"
            }

        return {
            "grounded": True,
            "reason": "sufficient_context",
            "documents": valid_documents
        }


    def validate_answer(self, answer, documents):
        if not answer:
            return {
                "grounded": False,
                "reason": "empty_answer"
            }

        answer = answer.strip()

        if len(answer) < 3:
            return {
                "grounded": False,
                "reason": "answer_too_short"
            }

        if not documents:
            return {
                "grounded": False,
                "reason": "no_context"
            }

        context = " ".join(
            document.get("text", "") for document in documents
        ).lower()

        answer_words = set(
            re.findall(r"\b[a-zA-Z]{3,}\b", answer.lower())
        )
        context_words = set(
            re.findall(r"\b[a-zA-Z]{3,}\b", context)
        )

        if not answer_words:
            return {
                "grounded": True,
                "reason": "no_verifiable_words",
                "overlap": 1.0
            }

        overlap = len(answer_words & context_words) / len(answer_words)

        if overlap < 0.15:
            return {
                "grounded": False,
                "reason": "low_context_overlap",
                "overlap": round(overlap, 3)
            }

        return {
            "grounded": True,
            "reason": "answer_grounded",
            "overlap": round(overlap, 3)
        }

    def final_decision(self, query_check, retrieval_check, answer_check):
        if not query_check["allowed"]:
            return {
                "allowed": False,
                "answer": "Sorry, I cannot process this request.",
                "reason": query_check["reason"]
            }

        if not retrieval_check["grounded"]:
            return {
                "allowed": False,
                "answer": "I don't have enough information in the provided dataset to answer this question.",
                "reason": retrieval_check["reason"]
            }

        if not answer_check["grounded"]:
            return {
                "allowed": False,
                "answer": "I don't have enough information in the provided dataset to answer this question.",
                "reason": answer_check["reason"]
            }

        return {
            "allowed": True,
            "answer": None,
            "reason": "passed"
        }