"""Тесты детерминированного эмбеддера."""

from app.domain.embeddings import CachedEmbedder, FakeEmbedder


class CountingEmbedder:
    def __init__(self) -> None:
        self.calls = 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        return [[float(len(text))] for text in texts]


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


def test_cached_embedder_reuses_vectors_and_preserves_order():
    base = CountingEmbedder()
    embedder = CachedEmbedder(base, backend="test", model="model-a")

    first = embedder.embed(["one", "two"])
    second = embedder.embed(["two", "three", "one"])

    assert first == [[3.0], [3.0]]
    assert second == [[3.0], [5.0], [3.0]]
    assert base.calls == 2


def test_cached_embedder_keeps_backend_and_model_isolated():
    base = CountingEmbedder()
    first = CachedEmbedder(base, backend="test", model="model-a")
    second = CachedEmbedder(base, backend="test", model="model-b")

    first.embed(["same"])
    second.embed(["same"])

    assert base.calls == 2
