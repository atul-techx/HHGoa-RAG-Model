import os
import re
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

NO_ANSWER = (
    "I don't have enough information "
    "in the provided dataset to answer "
    "this question."
)

STOP_WORDS = {
    "what", "is", "a", "an", "the", "who", "where", "when", "why", "how",
    "are", "was", "were", "did", "do", "does", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "about", "and", "or", "not", "tell", "me",
    "give", "definition", "meaning", "explain", "describe", "which"
}


DOMAIN_TERMS = [
    "corporation", "corporations", "company", "companies", "computer", "computers",
    "database", "databases", "artificial", "intelligence", "machine", "learning"
]


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def normalize_word(word):
    w = word.lower().strip("'s").strip('"').strip("'")
    if len(w) > 4 and w.endswith("ies"):
        w = w[:-3] + "y"
    elif len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    return w


def correct_query_typos(query):
    tokens = query.split()
    corrected_tokens = []
    for token in tokens:
        clean_t = re.sub(r'[^\w]', '', token).lower()
        if clean_t and clean_t not in STOP_WORDS and len(clean_t) >= 5:
            best_match = None
            min_dist = 99
            for term in DOMAIN_TERMS:
                dist = levenshtein(clean_t, term)
                if dist < min_dist:
                    min_dist = dist
                    best_match = term
            if min_dist <= 2 and best_match:
                new_token = re.sub(r'\b' + re.escape(clean_t) + r'\b', best_match, token, flags=re.IGNORECASE)
                corrected_tokens.append(new_token)
            else:
                corrected_tokens.append(token)
        else:
            corrected_tokens.append(token)
    return " ".join(corrected_tokens)


def clean_sentence(s):
    s = s.strip()
    s = re.sub(r'^(Rating Newest Oldest\.|Best Answer:|\s+)+', '', s, flags=re.IGNORECASE).strip()
    s = re.sub(r'\s*See more\.$', '', s, flags=re.IGNORECASE).strip()
    return s


from backend.neural_qa import ExtractiveQAModel

_neural_qa_engine = ExtractiveQAModel()

def extract_answer(query, contexts, model_mode="extractive_qa"):
    """
    Executes Extractive Neural QA Transformer Model inference over retrieved context passages.
    Returns neural answer span, transformer confidence score, and grounding details.
    """
    if not contexts:
        return None

    query_corr = correct_query_typos(query)
    qa_result = _neural_qa_engine.answer_question(query_corr, contexts)
    
    if qa_result and qa_result.get("grounded") and qa_result.get("confidence", 0.0) >= 0.10:
        return qa_result.get("answer")

    return None



class AnswerGenerator:

    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not API_KEY:
                raise RuntimeError("GEMINI_API_KEY not found in .env")
            from google import genai
            self._client = genai.Client(api_key=API_KEY)
        return self._client

    def generate(self, query, contexts, force_fallback=False):
        if not contexts:
            return {
                "answer": NO_ANSWER,
                "grounded": False,
                "method": "insufficient_context"
            }

        if not force_fallback:
            fast_answer = extract_answer(query, contexts)
            if fast_answer:
                return {
                    "answer": fast_answer,
                    "grounded": True,
                    "method": "local_context_answer"
                }
            else:
                return {
                    "answer": NO_ANSWER,
                    "grounded": False,
                    "method": "insufficient_context"
                }

        # Remote Gemini fallback
        if not API_KEY:
            return {
                "answer": NO_ANSWER,
                "grounded": False,
                "method": "gemini_fallback_unavailable"
            }

        context_parts = []
        for index, item in enumerate(contexts, start=1):
            text = item.get("text", "").strip()
            if text:
                context_parts.append(f"[Context {index}]\n{text}")

        context = "\n\n".join(context_parts)

        prompt = f"""
You are a grounded RAG question-answering assistant.

Answer ONLY from the provided context.

Rules:
- Do not use outside knowledge.
- Do not invent facts.
- If context is insufficient, return exactly:
{NO_ANSWER}
- Keep the answer concise.
- Prefer 1-2 sentences.

QUESTION:
{query}

CONTEXT:
{context}

ANSWER:
"""

        try:
            from google.genai import types
            client = self._get_client()
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=60,
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=0
                    )
                )
            )

            answer = response.text.strip() if response and response.text else ""

            if not answer or NO_ANSWER.lower() in answer.lower():
                return {
                    "answer": NO_ANSWER,
                    "grounded": False,
                    "method": "gemini_fallback"
                }

            return {
                "answer": answer,
                "grounded": True,
                "method": "gemini_fallback"
            }

        except Exception as error:
            return {
                "answer": NO_ANSWER,
                "grounded": False,
                "method": "gemini_fallback_error",
                "error": str(error)
            }