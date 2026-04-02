# subscription_data_pipeline

Пайплайн данных для подписок и платежей: OLTP PostgreSQL с тестовыми данными, генератор нагрузки (FastAPI), Apache Airflow, ClickHouse и Redis в Docker Compose.

## Требования

- [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/) (v2, команда `docker compose`)
- Для полного стека Airflow рекомендуется **не менее 4 ГБ RAM** и **2 CPU** (см. предупреждения контейнера `airflow-init` при старте)

## Подготовка окружения

1. Склонируйте репозиторий и перейдите в каталог проекта.

2. Создайте файл `.env` в корне (можно скопировать пример):

   ```bash
   cp .env.example .env
   ```

3. На **Linux** задайте `AIRFLOW_UID`, совпадающий с вашим пользователем, чтобы права на каталоги `logs`, `dags`, `plugins` не были root-only. В `.env.example` уже указан пример `1000` — при необходимости замените на `id -u`:

   ```bash
   echo "AIRFLOW_UID=$(id -u)" >> .env
   ```

## Запуск

### Весь стек (Airflow + OLTP + генератор + ClickHouse и т.д.)

```bash
docker compose up -d
```

Первый запуск может занять несколько минут: инициализируется база Airflow, поднимаются воркеры и планировщик.

### Только OLTP и генератор данных

Если нужны только PostgreSQL с схемой из `init-db/init.sql` и сервис генерации:

```bash
docker compose up -d oltp_source generator
```

Остальные сервисы (Airflow, Redis, второй Postgres и т.д.) не стартуют.

## Порты сервисов

| Сервис | Адрес | Назначение |
|--------|--------|------------|
| Генератор | http://localhost:8001 | **Swagger UI** http://localhost:8001/docs — интерактивная документация и вызовы API (старт/стоп генерации, статус) |
| OLTP PostgreSQL | `localhost:5433` | Базы `subscriptions_db` и `payments_db` (пользователь `postgres`, пароль `postgres`) |
| Airflow UI | http://localhost:8080 | Веб-интерфейс (логин/пароль по умолчанию из переменных `_AIRFLOW_WWW_USER_*`, `airflow` / `airflow`) |
| PostgreSQL (Airflow) | `localhost:5432` | Только для метаданных Airflow |
| ClickHouse HTTP | http://localhost:8123 | При необходимости OLAP-запросов |

Подключение генератора к OLTP внутри Compose уже задано в `docker-compose.yaml` (`SUB_DB_URL`, `PAY_DB_URL`).

## Инициализация баз OLTP

Скрипты из каталога `init-db/` монтируются в `oltp_source` как `/docker-entrypoint-initdb.d` и выполняются **один раз** при первом создании каталога данных PostgreSQL (создание БД, таблиц и начальных тарифов в `plans`).

Обычный перезапуск контейнеров **не** повторяет init. Чтобы заново применить `init.sql`, нужен новый пустой том данных у PostgreSQL OLTP: остановите сервисы и удалите том(а), куда пишет `oltp_source` (см. `docker volume ls`; при полном сбросе именованных томов проекта: `docker compose down -v` — осторожно, затронет и том Airflow `postgres-db-volume`, если он подключён).

## Генератор тестовых данных

После того как `oltp_source` здоров (`healthy`), сервис `generator` пишет пользователей, заказы, транзакции и подписки в соответствующие таблицы.

Пример запуска генерации (100 записей пользователей/заказов за задачу — см. параметр `count`):

```bash
curl -X POST "http://localhost:8001/start?count=100"
```

Статус:

```bash
curl http://localhost:8001/status
```

Остановка:

```bash
curl -X POST http://localhost:8001/stop
```

## Остановка

```bash
docker compose down
```

Чтобы также удалить именованный том метаданных Airflow (`postgres-db-volume`), используйте `docker compose down -v` (данные Airflow в UI и DAGs на диске в каталоге проекта сохраняются в `./logs`, `./dags` и т.д. согласно volume в compose).
