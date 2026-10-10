# Postgres в Docker — коротко и по делу

## Что вообще происходит

- **Образ (image)** — «упакованная программа» (здесь — сервер Postgres). Скачивается один раз.
- **Контейнер** — запущенный экземпляр образа. Его можно остановить и удалить, не задев данные.
- **Volume** — отдельное хранилище, которое переживает удаление контейнера. Сюда Postgres пишет данные.
- **Порт** — «дверь» наружу. Мы публикуем `5432:5432`, чтобы приложение и `psql` с хост-машины
  могли подключаться к базе как к `localhost:5432`.

## Что описано в `docker-compose.yml`

- сервис `db` (образ `postgres:16`) с логином/паролем/базой из переменных окружения и томом `pgdata`;
- сервис `adminer` — веб-интерфейс к базе (порт 8081, чтобы не мешать другим сервисам);
- при первом создании базы выполняется `docker/initdb/*.sql` — так создаётся вторая база
  `mini_assistant_test` для тестов.

## Основные команды

```bash
docker compose up -d          # поднять в фоне
docker compose ps             # что запущено
docker compose logs -f db     # логи базы (в т.ч. ошибки старта)
docker compose down           # остановить и удалить контейнеры (данные в volume остаются)
docker compose down -v        # + удалить volume (данные пропадут — иногда это нужно)
```

## Подключение

- Из приложения — строка `DATABASE_URL` из `.env`, например
  `postgresql+psycopg://mini:mini@localhost:5432/mini_assistant`.
- Из терминала: `docker exec -it mini_assistant_db psql -U mini -d mini_assistant`
  (внутри консоли: `\dt` — список таблиц, `\d chunks` — описание таблицы, `SELECT * FROM documents;`).
- Через браузер: `http://localhost:8081`, System: `PostgreSQL`, Server: `db`, логин/пароль `mini`/`mini`,
  база `mini_assistant`.

## Полезно знать

- Если порт 5432 занят (`address already in use`) — поменяй в `docker-compose.yml` левую часть на
  `"5433:5432"` и поправь `DATABASE_URL`.
- Ошибка `password authentication failed` — не совпали логин/пароль из `.env` и из базы (том уже создан
  со старыми значениями). Решение: `docker compose down -v` и поднять заново.
- Таблиц нет, пока не выполнена миграция: `alembic upgrade head`.
- Данные живут в томе `pgdata` и не пропадают при `docker compose down`.
