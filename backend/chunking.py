import re
from typing import List, Dict, Any

class ChunkingEngine:
    @staticmethod
    def chunk_fixed_size(text: str, chunk_size: int = 200) -> List[Dict[str, Any]]:
        """Fixed size naive chunking without overlap."""
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i:i + chunk_size].strip()
            if chunk_text:
                chunks.append({
                    "chunk_id": len(chunks),
                    "text": chunk_text,
                    "strategy": "fixed_size",
                    "start": i,
                    "end": i + len(chunk_text),
                    "length": len(chunk_text)
                })
        return chunks

    @staticmethod
    def chunk_overlap_optimized(text: str, chunk_size: int = 200, overlap: int = 50) -> List[Dict[str, Any]]:
        """Sliding window chunking with overlap handling to preserve boundary context."""
        chunks = []
        step = chunk_size - overlap
        if step <= 0:
            step = chunk_size
        for i in range(0, len(text), step):
            chunk_text = text[i:i + chunk_size].strip()
            if chunk_text:
                chunks.append({
                    "chunk_id": len(chunks),
                    "text": chunk_text,
                    "strategy": "overlap_optimized",
                    "start": i,
                    "end": i + len(chunk_text),
                    "overlap_size": overlap if i > 0 else 0,
                    "length": len(chunk_text)
                })
        return chunks

    @staticmethod
    def chunk_semantic(text: str, max_chunk_size: int = 250) -> List[Dict[str, Any]]:
        """Splits along semantic boundaries (paragraphs and sentences) instead of arbitrary token cuts."""
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_len = 0
        char_index = 0

        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            if current_len + len(sent) > max_chunk_size and current_chunk:
                chunk_str = " ".join(current_chunk)
                chunks.append({
                    "chunk_id": len(chunks),
                    "text": chunk_str,
                    "strategy": "semantic",
                    "sentence_count": len(current_chunk),
                    "start": char_index,
                    "end": char_index + len(chunk_str),
                    "length": len(chunk_str)
                })
                char_index += len(chunk_str) + 1
                current_chunk = [sent]
                current_len = len(sent)
            else:
                current_chunk.append(sent)
                current_len += len(sent) + 1

        if current_chunk:
            chunk_str = " ".join(current_chunk)
            chunks.append({
                "chunk_id": len(chunks),
                "text": chunk_str,
                "strategy": "semantic",
                "sentence_count": len(current_chunk),
                "start": char_index,
                "end": char_index + len(chunk_str),
                "length": len(chunk_str)
            })

        return chunks

    @staticmethod
    def chunk_metadata_aware(doc: Dict[str, Any], chunk_size: int = 200) -> List[Dict[str, Any]]:
        """Injects document metadata (title, category, doc_id) into every chunk text."""
        text = doc.get("text", "")
        title = doc.get("title", "Untitled Document")
        category = doc.get("category", "General")
        doc_id = doc.get("id", "doc_0")

        base_chunks = ChunkingEngine.chunk_overlap_optimized(text, chunk_size=chunk_size, overlap=40)
        metadata_chunks = []

        for c in base_chunks:
            meta_header = f"[Doc: {title} | Category: {category} | ID: {doc_id}]\n"
            enriched_text = meta_header + c["text"]
            metadata_chunks.append({
                "chunk_id": c["chunk_id"],
                "text": enriched_text,
                "raw_text": c["text"],
                "strategy": "metadata_aware",
                "doc_title": title,
                "doc_category": category,
                "doc_id": doc_id,
                "length": len(enriched_text)
            })

        return metadata_chunks

    @staticmethod
    def chunk_hierarchical(doc: Dict[str, Any], child_size: int = 100) -> List[Dict[str, Any]]:
        """Hierarchical parent-child chunking: small child chunks for precise vector matching mapped to full parent context."""
        text = doc.get("text", "")
        parent_id = doc.get("id", "parent_doc")
        
        # Children are small 100 char chunks
        child_chunks = []
        for i in range(0, len(text), child_size):
            child_text = text[i:i + child_size].strip()
            if child_text:
                child_chunks.append({
                    "chunk_id": len(child_chunks),
                    "text": child_text,
                    "parent_context": text,
                    "parent_id": parent_id,
                    "strategy": "hierarchical",
                    "doc_title": doc.get("title", ""),
                    "length": len(child_text)
                })

        return child_chunks

    @classmethod
    def process_document(cls, doc: Dict[str, Any], strategy: str = "semantic") -> List[Dict[str, Any]]:
        """Dispatches chunking based on selected strategy."""
        text = doc.get("text", "")
        if strategy == "fixed_size":
            chunks = cls.chunk_fixed_size(text)
        elif strategy == "overlap_optimized":
            chunks = cls.chunk_overlap_optimized(text)
        elif strategy == "metadata_aware":
            chunks = cls.chunk_metadata_aware(doc)
        elif strategy == "hierarchical":
            chunks = cls.chunk_hierarchical(doc)
        else: # default semantic
            chunks = cls.chunk_semantic(text)
            
        # Attach doc metadata
        for c in chunks:
            if "doc_id" not in c:
                c["doc_id"] = doc.get("id", "doc_0")
            if "doc_title" not in c:
                c["doc_title"] = doc.get("title", "")
        return chunks
