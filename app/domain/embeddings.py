"""Эмбеддинги.

TODO (M3): интерфейс, детерминированная заглушка для тестов и модель
sentence-transformers. Модель импортировать лениво (внутри класса), чтобы
тесты не тянули torch. Поведение — в SPEC.md.
"""

import hashlib
from typing import Any, Protocol, cast

from ..config import Settings


class Embedder(Protocol):
    """Превращает список текстов в список векторов."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


class FakeEmbedder:
    """TODO: детерминированные векторы из хэша текста."""

    def __init__(self, dim: int = 16) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [list(hashlib.sha256(text.encode("utf-8")).digest()[:self.dim]) for text in texts]

class CachedEmbedder:
    """Добавляет кэширование к любому объекту Embedder."""

    def __init__(self, embedder: Embedder, backend: str, model: str) -> None:
        self.embedder = embedder
        self.backend = backend
        self.model = model
        self.cache: dict[str, list[float]] = {}

    def _make_cache_key(self, text: str) -> str:
        value = f"{self.backend}:{self.model}:{text}"
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def embed(self, texts: list[str]) -> list[list[float]]:
        result: list[list[float]] = [[] for _ in texts]
        missing_texts: list[str] = []
        missing_indexes: list[int] = []

        for index, text in enumerate(texts):
            key = self._make_cache_key(text)
            if key in self.cache:
                result[index] = list(self.cache[key])
            else:
                missing_texts.append(text)
                missing_indexes.append(index)

        if missing_texts:
            new_embeddings = self.embedder.embed(missing_texts)
            if len(new_embeddings) != len(missing_texts):
                raise ValueError("Embedder returned a different number of embeddings than input texts.")

            for index, text, embedding in zip(missing_indexes, missing_texts, new_embeddings, strict=True):
                key = self._make_cache_key(text)
                vector = list(embedding)
                self.cache[key] = vector
                result[index] = list(vector)
        vectors: list[list[float]] = []
        for embedding in result:
            if embedding is not None:
                vectors.append(embedding)
        return vectors


class SentenceTransformerEmbedder:
    """TODO: настоящие эмбеддинги."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model: Any |None = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        """TODO: лениво импортировать и использовать sentence-transformers.
        """
        if self.model_name is None:
            raise ValueError("Model name is not specified.")
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            encoded = self._model.encode(texts, convert_to_numpy=True).tolist()
        return cast(list[list[float]], encoded)
        


def create_embedder(settings: Settings) -> Embedder:
    """TODO: выбрать бэкенд по настройкам."""
    if settings.embed_model is None or settings.embed_backend == "fake":
        base_embedder: Embedder = FakeEmbedder()
    else:
        base_embedder = SentenceTransformerEmbedder(model_name=settings.embed_model)

    return CachedEmbedder(embedder=base_embedder, backend=settings.embed_backend, model=settings.embed_model)
