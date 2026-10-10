"""Тесты разбиения текста на чанки."""

import pytest

from app.domain.chunking import chunk_text


def test_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   \n\n  ") == []


def test_short_paragraphs_merge_into_one_chunk():
    text = "Первый абзац.\n\nВторой абзац."
    chunks = chunk_text(text, size=100)
    assert chunks == ["Первый абзац.\n\nВторой абзац."]


def test_paragraphs_split_when_too_long():
    text = "A" * 60 + "\n\n" + "B" * 60
    chunks = chunk_text(text, size=80)
    assert chunks == ["A" * 60, "B" * 60]


def test_long_paragraph_splits_with_overlap():
    text = "x" * 1200
    chunks = chunk_text(text, size=500, overlap=50)
    assert chunks[0] == text[0:500]
    assert chunks[1] == text[450:950]
    assert chunks[2] == text[900:1200]
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_bad_parameters():
    with pytest.raises(ValueError):
        chunk_text("text", size=0)
    with pytest.raises(ValueError):
        chunk_text("text", size=100, overlap=100)
    with pytest.raises(ValueError):
        chunk_text("text", size=100, overlap=-1)
