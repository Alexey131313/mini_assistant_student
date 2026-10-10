"""Тесты настроек."""

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_defaults():
    settings = Settings(_env_file=None)
    assert settings.chunk_size == 500
    assert settings.chunk_overlap == 50
    assert settings.top_k == 3


def test_empty_string_becomes_none(monkeypatch):
    monkeypatch.setenv("TEST_DATABASE_URL", "")
    settings = Settings(_env_file=None)
    assert settings.test_database_url is None


def test_unknown_embed_backend_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, embed_backend="unknown")
