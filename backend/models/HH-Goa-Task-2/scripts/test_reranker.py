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

from app.reranker import Reranker


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

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

TOP_K_FAISS = 10

TOP_K_RERANK = 3


# --------------------------------------------------
# Load FAISS
# --------------------------------------------------

print("=" * 70)
print("LOADING FAISS INDEX")
print("=" * 70)

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

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("Embedding model loaded.")


# --------------------------------------------------
# Load Reranker
# --------------------------------------------------

reranker = Reranker()


# --------------------------------------------------
# Retrieval Function
# --------------------------------------------------

def retrieve(query):

    print("\n")
    print("=" * 70)
    print("QUERY")
    print("=" * 70)

    print(query)


    # --------------------------------------------------
    # Query Embedding
    # --------------------------------------------------

    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    )


    # --------------------------------------------------
    # FAISS Top 10
    # --------------------------------------------------

    scores, indices = index.search(
        query_embedding,
        TOP_K_FAISS
    )


    candidates = []


    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx < 0:
            continue

        item = metadata[idx].copy()

        # Store FAISS score
        item["faiss_score"] = float(
            score
        )

        candidates.append(
            item
        )


    print("\nFAISS candidates:")
    print(len(candidates))


    # --------------------------------------------------
    # Reranking
    # --------------------------------------------------

    print("\nRunning CrossEncoder reranker...")

    results = reranker.rerank(
        query=query,
        documents=candidates,
        top_k=TOP_K_RERANK
    )


    # --------------------------------------------------
    # Display Final Results
    # --------------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL RERANKED RESULTS")
    print("=" * 70)


    for rank, result in enumerate(
        results,
        start=1
    ):

        print("\n")
        print("-" * 70)

        print(
            f"RESULT #{rank}"
        )

        print(
            "FAISS Score:",
            round(
                result["faiss_score"],
                4
            )
        )

        print(
            "Reranker Score:",
            round(
                result["rerank_score"],
                4
            )
        )

        print(
            "Query ID:",
            result.get(
                "query_id"
            )
        )

        print(
            "Passage Index:",
            result.get(
                "passage_index"
            )
        )

        print(
            "Selected:",
            result.get(
                "is_selected"
            )
        )

        print("\nPASSAGE:")

        print(
            result.get(
                "text",
                ""
            )[:1000]
        )


    return results


# --------------------------------------------------
# Interactive Test
# --------------------------------------------------

print("\n")
print("=" * 70)
print("RERANKER TEST READY")
print("=" * 70)

print("Type a question.")
print("Type 'exit' to stop.")


while True:

    query = input(
        "\nQuestion: "
    ).strip()


    if query.lower() == "exit":

        print("\nTest stopped.")

        break


    if not query:

        print(
            "Please enter a question."
        )

        continue


    retrieve(query)