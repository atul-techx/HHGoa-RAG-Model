import re
from typing import List, Dict


def clean_text(text: str) -> str:
    """Clean unnecessary whitespace and formatting."""

    if not text:
        return ""

    text = str(text)

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def sentence_chunking(
    text: str,
    max_sentences: int = 4,
    overlap_sentences: int = 1
) -> List[str]:
    """
    Sentence-based chunking with overlap.
    """

    text = clean_text(text)

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []

    step = max(1, max_sentences - overlap_sentences)

    for i in range(0, len(sentences), step):

        chunk = " ".join(
            sentences[i:i + max_sentences]
        ).strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def word_chunking(
    text: str,
    chunk_size: int = 120,
    overlap: int = 30
) -> List[str]:
    """
    Word-based chunking with overlap.
    """

    text = clean_text(text)

    if not text:
        return []

    words = text.split()

    chunks = []

    step = max(1, chunk_size - overlap)

    for i in range(0, len(words), step):

        chunk_words = words[i:i + chunk_size]

        if not chunk_words:
            continue

        chunks.append(" ".join(chunk_words))

    return chunks


def semantic_style_chunking(
    text: str,
    max_words: int = 150
) -> List[str]:
    """
    Lightweight semantic-style chunking.

    Groups consecutive sentences while respecting
    a maximum word budget.
    """

    text = clean_text(text)

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current_chunk = []
    current_words = 0

    for sentence in sentences:

        sentence_words = sentence.split()
        sentence_length = len(sentence_words)

        if (
            current_words + sentence_length > max_words
            and current_chunk
        ):
            chunks.append(" ".join(current_chunk))

            current_chunk = []
            current_words = 0

        current_chunk.append(sentence)
        current_words += sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def create_multi_strategy_chunks(
    text: str,
    metadata: Dict = None
) -> List[Dict]:
    """
    Generate chunks using multiple strategies.

    Each chunk contains metadata describing
    which strategy produced it.
    """

    if metadata is None:
        metadata = {}

    all_chunks = []

    strategies = {
        "sentence": sentence_chunking(text),
        "word_overlap": word_chunking(text),
        "semantic": semantic_style_chunking(text)
    }

    for strategy_name, chunks in strategies.items():

        for index, chunk in enumerate(chunks):

            all_chunks.append({
                "text": chunk,
                "strategy": strategy_name,
                "chunk_index": index,
                "metadata": metadata
            })

    return all_chunks