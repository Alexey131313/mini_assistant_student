"""Тесты разбора SSE-строк OpenAI-совместимого стрима."""

import json

from app.domain.llm_client import extract_delta


def test_extract_delta():
    line = 'data: {"choices": [{"delta": {"content": "Привет"}}]}'
    assert extract_delta(line) == "Привет"


def test_extract_delta_done_and_other_lines():
    assert extract_delta("data: [DONE]") is None
    assert extract_delta(": keep-alive") is None
    assert extract_delta("") is None


def test_extract_delta_no_content():
    line = json.dumps({"choices": [{"delta": {}}]})
    assert extract_delta(f"data: {line}") is None
