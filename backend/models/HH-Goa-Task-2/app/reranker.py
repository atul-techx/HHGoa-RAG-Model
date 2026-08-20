class Reranker:

    def __init__(
        self,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.model_name = model_name
        self.model = None

    def _load_model(self):
        if self.model is None:
            print("Loading reranker model...")
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name)
            print("Reranker model loaded.")

    def rerank(
        self,
        query,
        documents,
        top_k=3
    ):
        if not documents:
            return []

        self._load_model()

        pairs = [
            (query, doc.get("text", "")) for doc in documents
        ]

        scores = self.model.predict(pairs)

        results = []
        for document, score in zip(documents, scores):
            result = document.copy()
            result["rerank_score"] = float(score)
            results.append(result)

        results.sort(key=lambda x: x["rerank_score"], reverse=True)
        return results[:top_k]