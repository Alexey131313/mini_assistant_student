"""Общая настройка тестов.

Интеграционные тесты требуют Postgres и переменной TEST_DATABASE_URL.
Если она не задана — они аккуратно пропускаются, unit-тесты всё равно идут.
"""

import os

import pytest

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if TEST_DATABASE_URL:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# В тестах не грузим настоящую модель и не ходим в реальный LLM.
os.environ.setdefault("EMBED_BACKEND", "fake")
os.environ.setdefault("LLM_BASE_URL", "http://llm.test/v1")
os.environ.setdefault("LLM_MODEL", "test-model")

requires_db = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL не задан — интеграционные тесты пропущены (подними Postgres из docker compose)",
)
