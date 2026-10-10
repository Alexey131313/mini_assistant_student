# mini_assistant

Учебный сервис: загружаем документы, ищем по ним нужные куски и просим LLM ответить.
Упрощённый аналог RAG-пайплайна: документ → чанки → эмбеддинги → база → top-k → LLM → ответ (и стриминг).

## Основные методы (HTTP)

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/health` | проверка состояния |
| POST | `/documents` | загрузить текст, разбить на чанки, сохранить |
| GET | `/documents` | список документов |
| GET | `/documents/{id}` | один документ |
| POST | `/ask` | вопрос → ответ + использованные куски |
| POST | `/ask/stream` | то же, но ответ приходит по частям (SSE) |

## Запуск

```bash
docker compose up -d          # Postgres + Adminer (http://localhost:8081)
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head           # создать таблицы
python -m app.main             # http://localhost:8000/docs
```

LLM — любой OpenAI-совместимый сервер (llama-server/vLLM) на адресе `LLM_BASE_URL`.

## Тесты

```bash
pytest                                     # unit; integration пропускаются, если нет TEST_DATABASE_URL
pytest -m "not integration"                # только unit
TEST_DATABASE_URL="postgresql+psycopg://mini:mini@localhost:5432/mini_assistant_test" pytest   # всё
```

## Структура

```
app/
├── main.py            # FastAPI: lifespan, зависимости, маршруты
├── config.py          # Settings + Config
├── logging_setup.py   # журналирование
├── schemas.py         # pydantic-модели API
├── db/                # Base, модели, repository
└── domain/            # chunking, embeddings, retrieval, llm_client
migrations/            # Alembic
tests/                 # unit + integration
```

Подробное задание — [SPEC.md](SPEC.md), ссылки на теорию — [docs/hints.md](docs/hints.md),
Postgres в Docker — [docs/postgres_docker.md](docs/postgres_docker.md).
