# mini_assistant — задание

Задача: собрать маленький сервис, который показывает сквозной пайплайн приложения с LLM.
Тесты в `tests/` описывают ожидаемое поведение. Очевидно - их не меняем.

Все команды — из корня проекта (если не указано явно). Теория — [docs/hints.md](docs/hints.md).

---

## 1. Как это работает

1. Приходит документ (`POST /documents`) → текст нарезается на чанки → для каждого считается вектор → всё сохраняется в Postgres.
2. Приходит вопрос (`POST /ask`) → считается вектор вопроса → ищутся ближайшие чанки (косинусовое сходство) → они подставляются в промпт, запрос к модели обогащается контекстом → ответ возвращается вместе с источниками.
3. `POST /ask/stream` делает то же самое, но отдаёт ответ кусочками (SSE).

---

## 2. Основные файлы (имена файлов обязательно такие — на них опираются тесты)

### Модули

| Модуль | Что должно быть |
|---|---|
| `app/config.py` | `Settings` (pydantic-settings), `Config`, `get_config()`, `reset_config()` |
| `app/logging_setup.py` | `setup_logging(level) -> Logger` |
| `app/schemas.py` | модели запросов/ответов (см. ниже) |
| `app/db/base.py` | `Base`, `make_engine(url)`, `make_session_factory(engine)` |
| `app/db/models.py` | `Document`, `Chunk` |
| `app/db/repository.py` | `create_document`, `list_documents`, `get_document`, `count_chunks`, `list_chunks` |
| `app/domain/chunking.py` | `chunk_text(text, size=500, overlap=50) -> list[str]` |
| `app/domain/embeddings.py` | `Embedder`, `FakeEmbedder`, `SentenceTransformerEmbedder`, `create_embedder(settings)` |
| `app/domain/retrieval.py` | `cosine(a, b) -> float`, `top_k(query, items, k) -> list[tuple[int, float]]` |
| `app/domain/llm_client.py` | `extract_delta(line) -> str | None`, `LLMClient` |
| `app/main.py` | `app = FastAPI(...)` + маршруты |

### Настройки `Settings` (имена полей)

`database_url`, `test_database_url` (необязательно; пустая строка = «не задано»), `llm_base_url`,
`llm_model`, `llm_api_key`, `llm_timeout`, `embed_backend` (`fake` или `sentence-transformers`),
`embed_model`, `chunk_size` (500), `chunk_overlap` (50), `top_k` (3), `log_level` (`INFO`).
Читаются из `.env`/окружения; лишние переменные игнорируются.

### Схемы API (pydantic-модели) `app/schemas.py`

Это описание формата JSON для запросов и ответов (не ML-модели). Они же дают валидацию
и автодокументацию в `/docs`.

| Модель | Поля |
|---|---|
| `HealthResponse` | `message` |
| `DocumentCreate` | `title` (1–255), `text` (непустой) |
| `DocumentOut` | `id`, `title`, `created_at`, `chunks` (число) |
| `AskRequest` | `question` (непустой), `k` (1–20, необязательно) |
| `SourceOut` | `chunk_id`, `document_id`, `score`, `text` |
| `AskResponse` | `answer`, `sources` |
| `ErrorResponse` | `detail` |

### Таблицы

| `documents` | |
|---|---|
| `id` | первичный ключ |
| `title` | строка ≤255 |
| `created_at` | дата-время, проставляется базой |

| `chunks` | |
|---|---|
| `id` | первичный ключ |
| `document_id` | ссылка на `documents`, каскадное удаление |
| `position` | номер чанка внутри документа (с 0) |
| `text` | текст чанка |
| `embedding` | вектор (JSON-список чисел) |

### Маршруты

| Маршрут | Поведение |
|---|---|
| `GET /health` | `{"message": "Healthy"}` |
| `POST /documents` | 201, тело `DocumentOut`; пустой `title` → 422; текст без чанков → 422 |
| `GET /documents` | список `DocumentOut` (новые сверху) |
| `GET /documents/{id}` | `DocumentOut` или 404 |
| `POST /ask` | `AskResponse`: `answer` + `sources` (top-k); ошибка LLM → 503 |
| `POST /ask/stream` | `text/event-stream`: события `data: {"token": ...}`, финал `data: [DONE]` |

---

## 3. Этапы

### M0. Каркас и инструменты

- Создать структуру пакетов `app/`, `app/db/`, `app/domain/` (файлы уже есть — заполнить).
- `app = FastAPI(...)`, `GET /health`.
- Запуск через `python -m app.main` (uvicorn внутри).
- `get_config()` возвращает один объект `Config`; `reset_config()` сбрасывает (нужно тестам).

**Приёмка:** `pytest tests/unit/test_config.py -q` зелёный; `GET /health` отвечает; ruff и mypy по проекту чисты.

### M1. Настройки и журналирование

- Реализовать `Settings` со всеми полями и проверкой «пустая строка → None» для `test_database_url`.
- `setup_logging(level)` настраивает вывод логов.

**Приёмка:** `pytest tests/unit -q` зелёный.

### M2. Postgres, модели, миграции, repository

- Поднять Postgres через `docker compose up -d` (см. `docs/postgres_docker.md`).
- `make_engine` / `make_session_factory`; модели `Document` и `Chunk` с нужными полями и связью.
- Alembic: `alembic.ini` уже есть; реализовать `migrations/env.py` и создать первую миграцию
  (`alembic revision --autogenerate -m "initial"`), накатить `alembic upgrade head`.
- `repository.*`: сохранение документа с чанками одной транзакцией, чтение списков/одного/числа.

**Приёмка:** `alembic upgrade head` проходит; таблицы видны в Adminer;
`TEST_DATABASE_URL=... pytest tests/integration/test_repository.py -q` зелёный.

### M3. Загрузка документов

- `chunk_text`: абзацы по пустой строке; короткие склеиваются до `size`; длинный абзац режется
  по `size` с перекрытием `overlap`; пустой текст → `[]`; неверные `size`/`overlap` → `ValueError`.
- `FakeEmbedder` (детерминированный, из хэша) и `SentenceTransformerEmbedder` (ленивый импорт модели).
- `POST /documents`, `GET /documents`, `GET /documents/{id}`.
- В lifespan создать движок, фабрику сессий, эмбеддер.

**Приёмка:** `pytest tests/unit/test_chunking.py tests/unit/test_embeddings.py -q`;
integration-тесты API (кроме `/ask`) зелёные.

### M4. Поиск и ответ

- `cosine` (нулевой вектор → 0.0; разная длина → `ValueError`), `top_k` (по убыванию, при равенстве — по id).
- `LLMClient.chat` через `httpx` к `{base_url}/chat/completions`.
- `POST /ask`: вектор вопроса → top-k → промпт с контекстом → ответ + источники.
- Ошибка обращения к LLM → 503.

**Приёмка:** `pytest tests/unit/test_retrieval.py tests/unit/test_llm_client.py -q`;
`tests/integration/test_api.py` зелёный (LLM в тестах подменяется).

### M5. Стриминг

- `LLMClient.stream` — разбор SSE-строк OpenAI (`data: {...}`, `[DONE]`).
- `POST /ask/stream` — `StreamingResponse` с событиями `data: {"token": ...}` и финалом `data: [DONE]`.

**Приёмка:** тест стриминга зелёный; вручную `curl -N` по живому LLM отдаёт кусочки.

### M6. Качество и эксплуатация

- Единый формат ошибок (`ErrorResponse`), аккуратные статусы.
- `ruff check .` и `mypy app` без замечаний.
- README с командами «с нуля»: compose → .env → миграции → запуск → тесты.

**Приёмка:** гейт зелёный; проект воспроизводится по README.

### M7. Запас (по желанию)

Один из вариантов: скрипт оценки (5 вопросов → время ответа и объём), гибридный поиск (BM25 + объединение
рангов), фоновый ingest, простой кэш эмбеддингов.

---

## 4. Правила

- Тесты и `docker-compose.yml` менять нельзя; `.env` не коммитить; секреты не писать в код, держать в переменных окружения.
- Сначала красим тесты в зеленый, потом наводим красоту (имена, разбиение функций etc.).
- Один шаг — один осмысленный коммит (или мини-MR): что сделал, почему, как проверил (сами имена коммитов кратко, тезисно, текст коммита - подробнее).
