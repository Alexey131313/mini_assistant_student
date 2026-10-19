"""Клиент к OpenAI-совместимому LLM.

TODO (M4–M5): обычный ответ и поток. Формат стрима — в SPEC.md и
tests/unit/test_llm_client.py.
"""

from collections.abc import AsyncIterator
import json

import httpx


def extract_delta(line: str) -> str | None:
    """TODO: достать кусочек текста из одной SSE-строки."""
    if not line.strip().startswith("data:"):
        return None
    data_str = line[6:].strip()
    if data_str == "[DONE]":
        return None
    try:
        dt = json.loads(data_str)
        choices = dt.get("choices", [])
        if not choices:
            return None
        delta = choices[0].get("delta", {})
        return delta.get("content")
    except json.JSONDecodeError:
        return None


class LLMClient:
    """Обёртка над /chat/completions."""

    def __init__(self, base_url: str, model: str, api_key: str = "dummy", timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    async def chat(self, messages: list[dict[str, str]]) -> str:
        """TODO: один полный ответ."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json = payload, headers = headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        """TODO: поток кусочков ответа."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json = payload, headers = headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    delta = extract_delta(line)
                    if delta is not None:
                        yield delta
