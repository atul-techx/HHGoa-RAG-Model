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


def extract_answer(query, contexts):
    """
    Fast local answer generation with lightweight typo tolerance.
    No API call. No LLM latency.
    Extracts concise, grounded answer directly from retrieved context ONLY when
    the selected retrieved context actually answers the user's question.
    """
    if not contexts:
        return None

    query_corr = correct_query_typos(query)
    query_raw = query_corr.strip()
    query_lower = query_raw.lower()

    # Extract non-stopword query keywords
    tokens = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", query_lower)
    keywords = [t for t in tokens if t not in STOP_WORDS]
    if not keywords:
        return None

    normalized_keywords = [normalize_word(kw) for kw in keywords]

    candidates = []

    for doc in contexts:
        faiss_score = doc.get("faiss_score", 0.0)
        text = doc.get("text", "").strip()
        if not text or len(text) < 10:
            continue

        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [clean_sentence(s) for s in sentences if len(s.strip()) > 5]

        for idx, sentence in enumerate(sentences):
            sentence_words = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", sentence.lower())
            sentence_norm = [normalize_word(w) for w in sentence_words]

            # 1. Keyword coverage check with typo tolerance
            matched_kws = set()
            for kw_norm in normalized_keywords:
                for w_norm in sentence_norm:
                    if (kw_norm == w_norm or
                        (len(kw_norm) >= 4 and len(w_norm) >= 4 and
                         (kw_norm in w_norm or w_norm in kw_norm or levenshtein(kw_norm, w_norm) <= 2))):
                        matched_kws.add(kw_norm)
                        break

            required_matches = len(normalized_keywords) if len(normalized_keywords) <= 2 else max(2, int(len(normalized_keywords) * 0.8))
            if len(matched_kws) < required_matches:
                continue

            # 2. Answerability & Subject Match Check
            kw_regex_parts = [r'\b' + re.escape(kw) + r"(s|'s|ies)?" + r'\b' for kw in keywords]
            kw_pattern = r'(' + '|'.join(kw_regex_parts) + r')'

            pattern_direct_is_a = r'^\s*(a|an|the)?\s*' + kw_pattern + r'\s+(is|are)\s+(a|an|the)?\b'
            pattern_start = r'^\s*(a|an|the)?\s*' + kw_pattern + r'\s+(definition|is|are|refers to|means|was|were|can be|has|consists of|incorporated|created|defined|owned|governed)\b'
            pattern_is_a = r'\b(a|an|the)?\s*' + kw_pattern + r'\s+(is|are|refers to|means|incorporated|defined as|created by)\b'
            pattern_a_is = r'\b(is|are)\s+(a|an|the)?\s*' + kw_pattern + r'\b'
            pattern_def_header = r'^\s*' + kw_pattern + r'\s*(definition|:|,)'

            s_lower = sentence.lower()
            is_match = (
                re.search(pattern_start, s_lower) or
                re.search(pattern_is_a, s_lower) or
                re.search(pattern_a_is, s_lower) or
                re.search(pattern_def_header, s_lower)
            )

            if not is_match:
                if faiss_score > 0.70 and len(matched_kws) == len(normalized_keywords):
                    explanatory = ["is", "are", "refers", "means", "incorporate", "defined", "create", "owned", "govern"]
                    if any(verb in sentence_norm for verb in explanatory):
                        is_match = True

            if is_match:
                score = 10.0 + len(matched_kws) * 5.0 + (faiss_score * 10.0)
                if re.search(pattern_direct_is_a, s_lower):
                    score += 20.0
                elif re.search(pattern_start, s_lower) or re.search(pattern_def_header, s_lower):
                    score += 10.0
                candidates.append((score, -idx, sentence))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][2]

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