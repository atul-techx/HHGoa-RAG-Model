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

# Common domain terms for typo correction
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
                # Substitute the corrected term preserving non-alphanumeric punctuation
                new_token = re.sub(r'\b' + re.escape(clean_t) + r'\b', best_match, token, flags=re.IGNORECASE)
                corrected_tokens.append(new_token)
            else:
                corrected_tokens.append(token)
        else:
            corrected_tokens.append(token)
    return " ".join(corrected_tokens)

print(f"Original: 'what is the coporation?' -> Corrected: '{correct_query_typos('what is the coporation?')}'")
