import sys
import os
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

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
    if not contexts:
        return None

    query_raw = query.strip()
    query_lower = query_raw.lower()

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

            # 1. Keyword coverage check with fuzzy/typo tolerance
            matched_kws = set()
            for kw_norm in normalized_keywords:
                for w_norm in sentence_norm:
                    if kw_norm == w_norm or (len(kw_norm) >= 4 and len(w_norm) >= 4 and (kw_norm in w_norm or w_norm in kw_norm or levenshtein(kw_norm, w_norm) <= 2)):
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

if __name__ == "__main__":
    from app.pipeline import RAGPipeline
    pipeline = RAGPipeline()

    test_qs = [
        "what is the corporation?",
        "what is the coporation?",
        "what is a company?",
        "what is artificial intelligence?",
        "what is a computer?",
        "what is machine learning?",
        "what is a database?"
    ]

    out_file = os.path.join(PROJECT_ROOT, "typo_eval_out.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        for q in test_qs:
            q_corr = correct_query_typos(q)
            docs = pipeline.retrieve(q_corr, top_k=3)
            ans = extract_answer(q, docs) or extract_answer(q_corr, docs)
            f.write(f"\nQUERY: '{q}'\n")
            f.write(f"RETRIEVED QUERY: '{q_corr}'\n")
            f.write(f"EXTRACTED ANSWER: {ans}\n")
    print("Wrote typo_eval_out.txt")
