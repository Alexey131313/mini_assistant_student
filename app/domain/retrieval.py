"""Поиск ближайших чанков.

TODO (M4): косинус и top-k. Точное поведение — в SPEC.md и
tests/unit/test_retrieval.py.
"""


import numpy as np


def cosine(a: list[float], b: list[float]) -> float:
    """TODO: косинусная близость; нулевой вектор → 0.0."""
    a = np.array(a)
    b = np.array(b)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    res = np.dot(a, b) / (na * nb)
    return res


def top_k(query: list[float], items: list[tuple[int, list[float]]], k: int) -> list[tuple[int, float]]:
    """TODO: топ-k пар (id, score)."""
    scores = [(item_id, cosine(query, embedding)) for item_id, embedding in items]
    scores.sort(key = lambda items: items[1], reverse = True)
    if k > len(scores):
        return scores
    return scores[:k]
