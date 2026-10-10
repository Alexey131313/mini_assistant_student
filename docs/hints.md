# Где искать (без готовых решений)

Общий принцип: сначала официальная документация и короткие туториалы, потом эксперименты в REPL.

## FastAPI

- Подойдёт раздел «Tutorial — User Guide»: приложение, маршруты, `Depends`, `response_model`, `lifespan`.
- Ищи: «FastAPI tutorial first steps», «FastAPI dependencies», «FastAPI lifespan», «FastAPI Testing».
- Для тестов API понадобится `fastapi.testclient.TestClient`.

## Pydantic и настройки

- «Pydantic v2 models», «pydantic-settings», «field validator».
- Обрати внимание на различия pydantic v1/v2 — сейчас нужен v2.

## SQLAlchemy 2.0 и Alembic

- «SQLAlchemy 2.0 ORM Quick Start»: `DeclarativeBase`, `Mapped`, `mapped_column`, `relationship`, `Session`.
- «Alembic tutorial»: `alembic init`, `alembic revision --autogenerate`, `alembic upgrade head`, `env.py`.
- Для Postgres драйвер — `psycopg` (версия 3); строка подключения начинается с `postgresql+psycopg://`.

## Postgres в Docker

- Локальный файл `docs/postgres_docker.md`.
- Ищи: «docker compose postgres», «adminer docker», «postgres environment variables».

## httpx и вызовы LLM

- «httpx async client», «httpx streaming response».
- Формат ответа OpenAI: `choices[0].message.content`, а для стрима — строки `data: {...}` и финальный `data: [DONE]`.
- Ищи: «OpenAI chat completions API stream format».

## SSE (Server-Sent Events)

- MDN «Using server-sent events»: формат `data: <текст>\n\n`.
- В FastAPI — `StreamingResponse(media_type="text/event-stream")`.

## Эмбеддинги

- `sentence-transformers`: «SentenceTransformer encode normalize_embeddings».
- Модель по умолчанию — `paraphrase-multilingual-MiniLM-L12-v2` (небольшая, понимает русский).
- Модель грузи один раз при старте (в lifespan), а не на каждый запрос.

## Как отлаживать

- Проще всего воспроизводить в REPL: запусти `python`, импортируй функцию, вызови на маленьких данных.
- Упал тест — читай снизу вверх: какое значение ожидалось и какое получилось.
- Для БД включи `echo=True` у движка на время отладки — увидишь SQL.
