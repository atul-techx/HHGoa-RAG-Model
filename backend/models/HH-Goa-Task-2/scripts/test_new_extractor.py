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

def normalize_word(word):
    w = word.lower().strip("'s").strip('"').strip("'")
    if len(w) > 4 and w.endswith("ies"):
        w = w[:-3] + "y"
    elif len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    return w

def clean_sentence(s):
    s = s.strip()
    # Remove common Web/QA artifacts
    s = re.sub(r'^(Rating Newest Oldest\.|Best Answer:|\s+)+', '', s, flags=re.IGNORECASE).strip()
    s = re.sub(r'\s*See more\.$', '', s, flags=re.IGNORECASE).strip()
    return s

def extract_answer(query, contexts):
    if not contexts:
        return None

    query_raw = query.strip()
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

            # Check keyword coverage
            matched_kws = set()
            for kw_norm in normalized_keywords:
                for w_norm in sentence_norm:
                    if kw_norm == w_norm or (len(kw_norm) >= 4 and len(w_norm) >= 4 and (kw_norm in w_norm or w_norm in kw_norm)):
                        matched_kws.add(kw_norm)
                        break

            required_matches = len(normalized_keywords) if len(normalized_keywords) <= 2 else max(2, int(len(normalized_keywords) * 0.8))
            if len(matched_kws) < required_matches:
                continue

            score = 10.0 + len(matched_kws) * 5.0 + (faiss_score * 5.0)

            first_words = sentence_words[:4]
            subject_in_start = any(kw in sentence_norm[:6] for kw in normalized_keywords)

            def_indicators = ["is", "are", "definition", "refers to", "means", "incorporated", "defined as", "known as", "created by"]
            has_def = any(ind in sentence_words for ind in def_indicators)

            is_another_subject_def = False
            if "is" in sentence_words:
                is_idx = sentence_words.index("is")
                kw_indices = [i for i, w in enumerate(sentence_norm) if any(kw == w or (len(kw)>=4 and kw in w) for kw in normalized_keywords)]
                if kw_indices and all(ki > is_idx for ki in kw_indices):
                    is_another_subject_def = True

            if re.search(r'^\w+\s*-\s*' + '|'.join(re.escape(kw) for kw in keywords), sentence, re.IGNORECASE):
                is_another_subject_def = True

            if is_another_subject_def:
                score -= 15.0

            if subject_in_start:
                score += 5.0
            if has_def:
                score += 3.0

            if score > 5.0:
                candidates.append((score, -idx, sentence))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_sentence = candidates[0][2]
        return best_sentence

    return None

if __name__ == "__main__":
    from app.pipeline import RAGPipeline
    pipeline = RAGPipeline()

    test_qs = [
        "what is a corporation?",
        "what is a company?",
        "what is artificial intelligence?",
        "what is a computer?",
        "what is machine learning?",
        "what is a database?",
        "what is the coporation"
    ]

    out_file = os.path.join(PROJECT_ROOT, "extractor_out.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        for q in test_qs:
            docs = pipeline.retrieve(q, top_k=3)
            ans = extract_answer(q, docs)
            f.write(f"\nQUERY: '{q}'\n")
            f.write(f"EXTRACTED: {ans}\n")
    print("Done writing extractor_out.txt")
