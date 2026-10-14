"""Cached local Sentence Transformers embeddings."""
from functools import lru_cache
from typing import Sequence
from config import EMBEDDING_MODEL

class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as exc:
                raise RuntimeError("Could not load the local embedding model. Check network access and installed dependencies.") from exc
        return self._model

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        values = self._get_model().encode(list(texts), normalize_embeddings=True, show_progress_bar=False)
        return values.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

@lru_cache(maxsize=2)
def get_embedder(model_name: str = EMBEDDING_MODEL) -> SentenceTransformerEmbedder:
    return SentenceTransformerEmbedder(model_name)
