"""Эмбеддинги.

TODO (M3): интерфейс, детерминированная заглушка для тестов и модель
sentence-transformers. Модель импортировать лениво (внутри класса), чтобы
тесты не тянули torch. Поведение — в SPEC.md.
"""

from typing import Protocol

from ..config import Settings


class Embedder(Protocol):
    """Превращает список текстов в список векторов."""

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class FakeEmbedder:
    """TODO: детерминированные векторы из хэша текста."""

    def __init__(self, dim: int = 16) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class SentenceTransformerEmbedder:
    """TODO: настоящие эмбеддинги."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


def create_embedder(settings: Settings) -> Embedder:
    """TODO: выбрать бэкенд по настройкам."""
    raise NotImplementedError
