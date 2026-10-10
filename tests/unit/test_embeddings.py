"""Тесты детерминированного эмбеддера."""

from app.domain.embeddings import FakeEmbedder


def test_same_text_same_vector():
    embedder = FakeEmbedder(dim=8)
    first = embedder.embed(["привет"])[0]
    second = embedder.embed(["привет"])[0]
    assert first == second
    assert len(first) == 8


def test_different_texts_differ():
    embedder = FakeEmbedder(dim=8)
    a, b = embedder.embed(["один", "два"])
    assert a != b


def test_order_preserved_and_empty():
    embedder = FakeEmbedder(dim=4)
    vectors = embedder.embed(["a", "b", "c"])
    assert len(vectors) == 3
    assert embedder.embed([]) == []
