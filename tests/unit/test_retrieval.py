"""Тесты косинусной близости и top-k."""

import pytest

from app.domain.retrieval import cosine, top_k


def test_cosine_basic():
    assert cosine([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert cosine([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)


def test_cosine_zero_vector():
    assert cosine([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_cosine_length_mismatch():
    with pytest.raises(ValueError):
        cosine([1.0], [1.0, 2.0])


def test_top_k_order_and_ties():
    query = [1.0, 0.0]
    items = [(10, [1.0, 0.0]), (20, [0.0, 1.0]), (30, [1.0, 0.0])]

    top2 = top_k(query, items, 2)
    assert [item_id for item_id, _ in top2] == [10, 30]
    assert top2[0][1] == pytest.approx(1.0)

    assert top_k(query, items, 0) == []

    all_items = top_k(query, items, 99)
    assert [item_id for item_id, _ in all_items] == [10, 30, 20]
    assert all_items[2][1] == pytest.approx(0.0)
