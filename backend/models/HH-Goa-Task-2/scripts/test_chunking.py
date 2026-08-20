import sys
import os

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
from huggingface_hub import hf_hub_download

from app.chunker import create_multi_strategy_chunks


# --------------------------------------------------
# Configuration
# --------------------------------------------------

REPO_ID = "ai4bharat/MSMARCO-XI"
FILE_NAME = "validation/hinval.parquet"

SAMPLE_ROWS = 3


# --------------------------------------------------
# Download Parquet File
# --------------------------------------------------

print("Downloading Hindi validation file...")

file_path = hf_hub_download(
    repo_id=REPO_ID,
    filename=FILE_NAME,
    repo_type="dataset"
)

print("\nFile downloaded successfully!")
print("Local path:")
print(file_path)


# --------------------------------------------------
# Open Parquet File
# --------------------------------------------------

print("\nOpening Parquet file...")

parquet_file = pq.ParquetFile(file_path)

print("\nParquet file opened successfully!")

print("Number of row groups:")
print(parquet_file.num_row_groups)

print("Number of rows:")
print(parquet_file.metadata.num_rows)


# --------------------------------------------------
# Read only a small batch
# --------------------------------------------------

print("\nReading first batch...")

batch_reader = parquet_file.iter_batches(
    batch_size=10
)

batch = next(batch_reader)

print("Batch loaded successfully!")

print("Rows in batch:")
print(batch.num_rows)

print("\nColumns:")
print(batch.schema.names)


# --------------------------------------------------
# Convert only small batch to Python
# --------------------------------------------------

records = batch.to_pylist()


# --------------------------------------------------
# Test first 3 records
# --------------------------------------------------

for record_number, record in enumerate(
    records[:SAMPLE_ROWS],
    start=1
):

    print("\n")
    print("=" * 70)
    print(f"RECORD {record_number}")
    print("=" * 70)

    # --------------------------------------------------
    # Basic information
    # --------------------------------------------------

    query = record.get("query", "")
    english_query = record.get("Eng_Query", "")

    answer = record.get("Answer", "")
    english_answer = record.get("Eng_Answer", "")

    query_id = record.get("query_id")
    query_type = record.get("query_type")

    print("\nQUERY:")
    print(query)

    print("\nENGLISH QUERY:")
    print(english_query)

    print("\nANSWER:")
    print(answer)

    print("\nENGLISH ANSWER:")
    print(english_answer)

    print("\nQUERY ID:")
    print(query_id)

    print("\nQUERY TYPE:")
    print(query_type)


    # --------------------------------------------------
    # Passages
    # --------------------------------------------------

    passages = record.get("passages") or {}

    english_passages = passages.get(
        "English_passages",
        []
    )

    translated_passages = passages.get(
        "Translated_passages",
        []
    )

    selected_flags = passages.get(
        "is_selected",
        []
    )

    print("\nNUMBER OF ENGLISH PASSAGES:")
    print(len(english_passages))

    print("\nSELECTED FLAGS:")
    print(selected_flags)


    # --------------------------------------------------
    # Chunk first English passage
    # --------------------------------------------------

    if english_passages:

        text = english_passages[0]

        print("\nFIRST ENGLISH PASSAGE:")
        print("-" * 70)
        print(text[:1000])


        # --------------------------------------------------
        # Multi-strategy chunking
        # --------------------------------------------------

        chunks = create_multi_strategy_chunks(
            text,
            metadata={
                "query_id": query_id,
                "query_type": query_type,
                "source_lang": record.get("source_lang"),
                "target_lang": record.get("target_lang"),
                "language_file": "hinval"
            }
        )


        print("\n")
        print("-" * 70)
        print("CHUNKING RESULTS")
        print("-" * 70)

        print("\nTOTAL CHUNKS:")
        print(len(chunks))


        # --------------------------------------------------
        # Display chunks
        # --------------------------------------------------

        for chunk_number, chunk in enumerate(
            chunks[:6],
            start=1
        ):

            print("\n" + "-" * 50)

            print(f"CHUNK {chunk_number}")

            print("Strategy:")
            print(chunk["strategy"])

            print("Chunk Index:")
            print(chunk["chunk_index"])

            print("Text:")
            print(chunk["text"][:500])

    else:

        print("\nNo English passages found.")


# --------------------------------------------------
# Completed
# --------------------------------------------------

print("\n")
print("=" * 70)
print("DIRECT PARQUET + CHUNKING TEST COMPLETED")
print("=" * 70)