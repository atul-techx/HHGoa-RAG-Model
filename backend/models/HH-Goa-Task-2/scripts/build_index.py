import sys
import os
import json
import hashlib

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

import pyarrow.parquet as pq
import faiss

from huggingface_hub import hf_hub_download
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Configuration
# --------------------------------------------------

REPO_ID = "ai4bharat/MSMARCO-XI"

FILE_NAME = "validation/hinval.parquet"

MAX_RECORDS = 100

BATCH_SIZE = 32

EMBEDDING_BATCH_SIZE = 32

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

INDEX_DIR = os.path.join(
    PROJECT_ROOT,
    "index"
)

INDEX_FILE = os.path.join(
    INDEX_DIR,
    "rag.index"
)

METADATA_FILE = os.path.join(
    INDEX_DIR,
    "metadata.json"
)


# --------------------------------------------------
# Create index directory
# --------------------------------------------------

os.makedirs(
    INDEX_DIR,
    exist_ok=True
)


# --------------------------------------------------
# Download Dataset
# --------------------------------------------------

print("=" * 70)
print("DOWNLOADING DATASET")
print("=" * 70)

file_path = hf_hub_download(
    repo_id=REPO_ID,
    filename=FILE_NAME,
    repo_type="dataset"
)

print("\nDataset file:")
print(file_path)


# --------------------------------------------------
# Open Parquet
# --------------------------------------------------

print("\nOpening Parquet...")

parquet_file = pq.ParquetFile(
    file_path
)

print("Total dataset rows:")
print(parquet_file.metadata.num_rows)


# --------------------------------------------------
# Load Embedding Model
# --------------------------------------------------

print("\nLoading embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)

print("Embedding model loaded.")


# --------------------------------------------------
# Storage
# --------------------------------------------------

texts = []

metadata = []

seen_hashes = set()


# --------------------------------------------------
# Read Dataset
# --------------------------------------------------

print("\nProcessing records...")

processed_records = 0

for batch in parquet_file.iter_batches(
    batch_size=BATCH_SIZE
):

    records = batch.to_pylist()

    for record in records:

        if processed_records >= MAX_RECORDS:
            break

        processed_records += 1

        query_id = record.get(
            "query_id"
        )

        query = record.get(
            "query",
            ""
        )

        query_type = record.get(
            "query_type",
            ""
        )

        source_lang = record.get(
            "source_lang",
            ""
        )

        target_lang = record.get(
            "target_lang",
            ""
        )


        passages = record.get(
            "passages"
        ) or {}


        english_passages = passages.get(
            "English_passages",
            []
        )


        selected_flags = passages.get(
            "is_selected",
            []
        )


        # --------------------------------------------------
        # Process ALL passages
        # --------------------------------------------------

        for passage_index, passage in enumerate(
            english_passages
        ):

            if not passage:
                continue


            text = str(
                passage
            ).strip()


            if not text:
                continue


            # --------------------------------------------------
            # Deduplication
            # --------------------------------------------------

            text_hash = hashlib.md5(
                text.encode(
                    "utf-8"
                )
            ).hexdigest()


            if text_hash in seen_hashes:
                continue


            seen_hashes.add(
                text_hash
            )


            # --------------------------------------------------
            # Selected flag
            # --------------------------------------------------

            is_selected = 0

            if passage_index < len(
                selected_flags
            ):

                is_selected = int(
                    selected_flags[
                        passage_index
                    ]
                )


            # --------------------------------------------------
            # Store text
            # --------------------------------------------------

            texts.append(
                text
            )


            # --------------------------------------------------
            # Store metadata
            # --------------------------------------------------

            metadata.append(
    {
        "text": text,
        "query_id": query_id,
        "query": query,
        "query_type": query_type,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "passage_index": passage_index,
        "is_selected": is_selected,
        "source_file": FILE_NAME,
        "text_hash": text_hash
    }
)
            


    if processed_records >= MAX_RECORDS:
        break


    print(
        f"Processed records: {processed_records}"
    )


# --------------------------------------------------
# Statistics
# --------------------------------------------------

print("\n")
print("=" * 70)
print("PROCESSING COMPLETE")
print("=" * 70)

print(
    "Records processed:",
    processed_records
)

print(
    "Unique passages:",
    len(texts)
)


# --------------------------------------------------
# Check data
# --------------------------------------------------

if not texts:

    print("\nERROR: No passages found.")

    sys.exit(1)


# --------------------------------------------------
# Create Embeddings
# --------------------------------------------------

print("\nCreating embeddings...")

embeddings = model.encode(
    texts,
    batch_size=EMBEDDING_BATCH_SIZE,
    show_progress_bar=True,
    normalize_embeddings=True
)


print("\nEmbeddings created.")

print(
    "Embedding shape:",
    embeddings.shape
)


# --------------------------------------------------
# Create FAISS Index
# --------------------------------------------------

print("\nCreating FAISS index...")

dimension = embeddings.shape[1]


index = faiss.IndexFlatIP(
    dimension
)


index.add(
    embeddings
)


print(
    "FAISS vectors:",
    index.ntotal
)


# --------------------------------------------------
# Save FAISS Index
# --------------------------------------------------

faiss.write_index(
    index,
    INDEX_FILE
)


print("\nFAISS index saved:")
print(INDEX_FILE)


# --------------------------------------------------
# Save Metadata
# --------------------------------------------------

with open(
    METADATA_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        metadata,
        file,
        ensure_ascii=False,
        indent=2
    )


print("\nMetadata saved:")
print(METADATA_FILE)


# --------------------------------------------------
# Final
# --------------------------------------------------

print("\n")
print("=" * 70)
print("VECTOR INDEX BUILD COMPLETED")
print("=" * 70)

print(
    f"Vectors: {index.ntotal}"
)

print(
    f"Metadata entries: {len(metadata)}"
)