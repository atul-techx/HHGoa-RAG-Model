import sys
import os

# --------------------------------------------------
# Add project root to Python path
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

BATCH_SIZE = 10


# --------------------------------------------------
# Download Dataset File
# --------------------------------------------------

print("Downloading Hindi validation dataset...")

file_path = hf_hub_download(
    repo_id=REPO_ID,
    filename=FILE_NAME,
    repo_type="dataset"
)

print("\nDataset file ready:")
print(file_path)


# --------------------------------------------------
# Open Parquet
# --------------------------------------------------

parquet_file = pq.ParquetFile(file_path)

print("\nTotal rows:")
print(parquet_file.metadata.num_rows)


# --------------------------------------------------
# Read Small Batch
# --------------------------------------------------

print("\nReading first batch...")

batch_reader = parquet_file.iter_batches(
    batch_size=BATCH_SIZE
)

batch = next(batch_reader)

records = batch.to_pylist()

print("Batch loaded:", len(records), "records")


# --------------------------------------------------
# Process Records
# --------------------------------------------------

for record_number, record in enumerate(
    records,
    start=1
):

    print("\n")
    print("=" * 70)
    print(f"RECORD {record_number}")
    print("=" * 70)


    # --------------------------------------------------
    # Basic Metadata
    # --------------------------------------------------

    query_id = record.get("query_id")

    query = record.get(
        "query",
        ""
    )

    english_query = record.get(
        "Eng_Query",
        ""
    )

    answer = record.get(
        "Answer",
        ""
    )

    query_type = record.get(
        "query_type",
        ""
    )


    # --------------------------------------------------
    # Passage Data
    # --------------------------------------------------

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
    # Print Query
    # --------------------------------------------------

    print("\nQuery ID:")
    print(query_id)

    print("\nQuery:")
    print(query)

    print("\nEnglish Query:")
    print(english_query)

    print("\nQuery Type:")
    print(query_type)

    print("\nAnswer:")
    print(answer)


    # --------------------------------------------------
    # Selected Passages
    # --------------------------------------------------

    selected_passages = []

    for index, passage in enumerate(
        english_passages
    ):

        is_selected = False

        if index < len(selected_flags):

            is_selected = (
                selected_flags[index] == 1
            )

        if is_selected:

            selected_passages.append(
                {
                    "passage_index": index,
                    "text": passage
                }
            )


    # --------------------------------------------------
    # Print Passage Statistics
    # --------------------------------------------------

    print("\nTotal passages:")
    print(len(english_passages))

    print("\nSelected passages:")
    print(len(selected_passages))


    # --------------------------------------------------
    # Process Selected Passages
    # --------------------------------------------------

    for selected in selected_passages:

        passage_index = selected[
            "passage_index"
        ]

        text = selected[
            "text"
        ]


        print("\n")
        print("-" * 70)

        print(
            f"SELECTED PASSAGE #{passage_index}"
        )

        print("-" * 70)

        print(text[:500])


        # --------------------------------------------------
        # Generate Chunks
        # --------------------------------------------------

        chunks = create_multi_strategy_chunks(
            text,
            metadata={
                "query_id": query_id,
                "query": query,
                "english_query": english_query,
                "query_type": query_type,
                "passage_index": passage_index,
                "is_selected": True,
                "source_file": FILE_NAME
            }
        )


        print("\nGenerated chunks:")
        print(len(chunks))


        # --------------------------------------------------
        # Show First 3 Chunks
        # --------------------------------------------------

        for chunk_number, chunk in enumerate(
            chunks[:3],
            start=1
        ):

            print("\nChunk:", chunk_number)

            print(
                "Strategy:",
                chunk["strategy"]
            )

            print(
                "Passage:",
                passage_index
            )

            print(
                "Text:",
                chunk["text"][:300]
            )


# --------------------------------------------------
# Completed
# --------------------------------------------------

print("\n")
print("=" * 70)
print("SELECTED PASSAGE TEST COMPLETED")
print("=" * 70)