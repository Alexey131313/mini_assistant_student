"""HTTP-сервис мини-ассистента.

TODO (M0–M5): конфигурация, зависимости, lifespan (движок БД, эмбеддер,
LLM-клиент) и маршруты. Список маршрутов и их поведение — в SPEC.md.
"""

from fastapi import FastAPI

app = FastAPI(title="mini_assistant", version="1.0.0")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
