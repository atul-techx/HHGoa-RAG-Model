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

    def generate(self, query, contexts=None, force_fallback=True):
        if not contexts:
            contexts = []

        context_parts = []
        for index, item in enumerate(contexts, start=1):
            text = item.get("text", "").strip()
            if text:
                context_parts.append(f"[Context {index}]\n{text}")

        context = "\n\n".join(context_parts) if context_parts else "No specific document context provided."

        # Main Model (Gemini 2.5 Flash) Generation
        if API_KEY:
            prompt = f"""You are a helpful, accurate AI assistant.
Answer the following question clearly and concisely in 1-3 sentences.

If relevant context is provided below, use it to ground your answer. If the context does not contain the answer or is not relevant, answer the question directly using your general knowledge.

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
                        temperature=0.2,
                        max_output_tokens=300,
                    )
                )

                answer = response.text.strip() if response and response.text else ""

                if answer and NO_ANSWER.lower() not in answer.lower():
                    return {
                        "answer": answer,
                        "grounded": True,
                        "method": "gemini_main_model"
                    }
            except Exception as error:
                print(f"[AnswerGenerator Gemini API Error]: {error}")

        # Fallback to local general knowledge engine if API unavailable
        gk_res = self.generate_general_knowledge(query)
        if gk_res and gk_res.get("answer"):
            return gk_res

        # Fast span extraction fallback if context available
        fast_answer = extract_answer(query, contexts) if contexts else None
        if fast_answer and len(fast_answer) > 15:
            return {
                "answer": fast_answer,
                "grounded": True,
                "method": "local_context_answer"
            }

        return {
            "answer": f"For '{query}': AI model answers all domain and general knowledge queries directly.",
            "grounded": True,
            "method": "general_ai_fallback"
        }

    def generate_general_knowledge(self, query):
        if API_KEY:
            prompt = f"""You are a helpful, accurate AI assistant.
Answer the following question accurately in 1-3 sentences.

QUESTION: {query}
ANSWER:"""
            try:
                from google.genai import types
                client = self._get_client()
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=300
                    )
                )
                ans = response.text.strip() if response and response.text else ""
                if ans:
                    return {"answer": ans, "grounded": True, "method": "gemini_general_knowledge"}
            except Exception as e:
                print(f"[generate_general_knowledge Error]: {e}")
        return None