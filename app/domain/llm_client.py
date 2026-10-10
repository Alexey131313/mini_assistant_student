"""Клиент к OpenAI-совместимому LLM.

TODO (M4–M5): обычный ответ и поток. Формат стрима — в SPEC.md и
tests/unit/test_llm_client.py.
"""

from collections.abc import AsyncIterator


def extract_delta(line: str) -> str | None:
    """TODO: достать кусочек текста из одной SSE-строки."""
    raise NotImplementedError


class LLMClient:
    """Обёртка над /chat/completions."""

    def __init__(self, base_url: str, model: str, api_key: str = "dummy", timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    async def chat(self, messages: list[dict[str, str]]) -> str:
        """TODO: один полный ответ."""
        raise NotImplementedError

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        """TODO: поток кусочков ответа."""
        raise NotImplementedError
