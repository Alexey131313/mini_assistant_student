"""Эмбеддинги.

TODO (M3): интерфейс, детерминированная заглушка для тестов и модель
sentence-transformers. Модель импортировать лениво (внутри класса), чтобы
тесты не тянули torch. Поведение — в SPEC.md.
"""

from typing import Protocol

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
        return [[float(hash(text) % 1000) / 1000] * self.dim for text in texts]


class SentenceTransformerEmbedder:
    """TODO: настоящие эмбеддинги."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        """TODO: лениво импортировать и использовать sentence-transformers.
        """
        if self.model_name is None:
            raise ValueError("Model name is not specified.")
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model.encode(texts, convert_to_numpy=True).tolist()
        


def create_embedder(settings: Settings) -> Embedder:
    """TODO: выбрать бэкенд по настройкам."""
    if settings.embed_model is None or settings.embed_backend == "fake":
        return FakeEmbedder()
    else:
        return SentenceTransformerEmbedder(model_name=settings.embed_model)
