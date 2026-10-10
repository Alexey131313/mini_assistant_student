"""Тесты HTTP API."""

import httpx
import pytest
import respx

pytestmark = pytest.mark.integration


def _load_document(client, text: str, title: str = "Документ") -> dict:
    response = client.post("/documents", json={"title": title, "text": text})
    assert response.status_code == 201, response.text
    return response.json()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "Healthy"}


def test_create_and_list_documents(client):
    document = _load_document(client, "Первый абзац.\n\nВторой абзац.")
    assert document["chunks"] >= 1

    listing = client.get("/documents")
    assert listing.status_code == 200
    assert any(item["id"] == document["id"] for item in listing.json())

    detail = client.get(f"/documents/{document['id']}")
    assert detail.status_code == 200
    assert detail.json()["title"] == "Документ"


def test_get_missing_document(client):
    assert client.get("/documents/99999").status_code == 404


def test_validation_error_on_empty_title(client):
    response = client.post("/documents", json={"title": "", "text": "текст"})
    assert response.status_code == 422


@respx.mock
def test_ask_returns_answer_and_sources(client):
    _load_document(client, "Столица Франции — Париж.")
    respx.post("http://llm.test/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "Париж"}}]})
    )

    response = client.post("/ask", json={"question": "Столица Франции?", "k": 1})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["answer"] == "Париж"
    assert len(body["sources"]) == 1


def test_ask_stream(client):
    _load_document(client, "Факт для потока.")

    class FakeLLM:
        async def stream(self, messages):
            for token in ["Пар", "иж"]:
                yield token

    client.app.state.llm = FakeLLM()
    response = client.post("/ask/stream", json={"question": "Какой город?"})
    assert response.status_code == 200
    assert '"token"' in response.text
    assert "data: [DONE]" in response.text
