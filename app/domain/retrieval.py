"""Поиск ближайших чанков.

TODO (M4): косинус и top-k. Точное поведение — в SPEC.md и
tests/unit/test_retrieval.py.
"""


def cosine(a: list[float], b: list[float]) -> float:
    """TODO: косинусная близость; нулевой вектор → 0.0."""
    raise NotImplementedError


def top_k(query: list[float], items: list[tuple[int, list[float]]], k: int) -> list[tuple[int, float]]:
    """TODO: топ-k пар (id, score)."""
    raise NotImplementedError
