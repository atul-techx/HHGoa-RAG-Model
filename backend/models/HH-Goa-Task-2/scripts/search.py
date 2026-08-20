import sys
import os
import json

# --------------------------------------------------
# Project root
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)


# --------------------------------------------------
# Imports
# --------------------------------------------------

import faiss

from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INDEX_FILE = os.path.join(
    PROJECT_ROOT,
    "index",
    "rag.index"
)

METADATA_FILE = os.path.join(
    PROJECT_ROOT,
    "index",
    "metadata.json"
)

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

TOP_K = 5


# --------------------------------------------------
# Load FAISS Index
# --------------------------------------------------

print("=" * 70)
print("LOADING RAG INDEX")
print("=" * 70)

if not os.path.exists(INDEX_FILE):

    print("ERROR: FAISS index not found.")

    sys.exit(1)


index = faiss.read_index(
    INDEX_FILE
)

print(
    "FAISS vectors:",
    index.ntotal
)


# --------------------------------------------------
# Load Metadata
# --------------------------------------------------

if not os.path.exists(METADATA_FILE):

    print("ERROR: Metadata file not found.")

    sys.exit(1)


with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as file:

    metadata = json.load(file)


print(
    "Metadata entries:",
    len(metadata)
)


# --------------------------------------------------
# Load Embedding Model
# --------------------------------------------------

print("\nLoading embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)

print("Embedding model loaded.")


# --------------------------------------------------
# Search Function
# --------------------------------------------------

def search(query, top_k=TOP_K):

    print("\n")
    print("=" * 70)
    print("SEARCH QUERY")
    print("=" * 70)

    print(query)


    # --------------------------------------------------
    # Create Query Embedding
    # --------------------------------------------------

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )


    # --------------------------------------------------
    # FAISS Search
    # --------------------------------------------------

    scores, indices = index.search(
        query_embedding,
        top_k
    )


    # --------------------------------------------------
    # Display Results
    # --------------------------------------------------

    results = []


    for rank, (score, idx) in enumerate(
        zip(
            scores[0],
            indices[0]
        ),
        start=1
    ):

        if idx < 0:
            continue


        item = metadata[idx]


        result = {
            "rank": rank,
            "score": float(score),
            "query_id": item.get(
                "query_id"
            ),
            "query": item.get(
                "query"
            ),
            "passage_index": item.get(
                "passage_index"
            ),
            "is_selected": item.get(
                "is_selected"
            ),
            "source_lang": item.get(
                "source_lang"
            ),
            "target_lang": item.get(
                "target_lang"
            )
        }


        results.append(
            result
        )


        print("\n")
        print("-" * 70)

        print(
            f"RESULT #{rank}"
        )

        print(
            "Similarity Score:",
            round(
                float(score),
                4
            )
        )

        print(
            "Query ID:",
            item.get("query_id")
        )

        print(
            "Passage Index:",
            item.get(
                "passage_index"
            )
        )

        print(
            "Selected:",
            item.get(
                "is_selected"
            )
        )

        print(
            "Original Query:",
            item.get(
                "query"
            )
        )

        print(
            "Source Language:",
            item.get(
                "source_lang"
            )
        )

        print(
            "Target Language:",
            item.get(
                "target_lang"
            )
        )

    return results


# --------------------------------------------------
# Interactive Search
# --------------------------------------------------

print("\n")
print("=" * 70)
print("RAG RETRIEVAL SYSTEM READY")
print("=" * 70)

print("\nType a question to search.")
print("Type 'exit' to stop.")


while True:

    user_query = input(
        "\nQuestion: "
    ).strip()


    if user_query.lower() == "exit":

        print("\nSearch stopped.")

        break


    if not user_query:

        print(
            "Please enter a question."
        )

        continue


    search(
        user_query
    )
    