# Используем версию Python из вашего pyproject.toml
FROM python:3.12-slim

# Настройки Python: не создавать .pyc файлы, не буферизировать логи
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# Устанавливаем системные зависимости для psycopg2 и curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Копируем только файлы зависимостей для кэширования слоев
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости (без dev-пакетов, чтобы образ был легче)
RUN poetry install --only main --no-root

# Копируем весь проект
COPY . .

# Команда запуска
CMD ["uvicorn", "generator.main:app", "--host", "0.0.0.0", "--port", "8000"]
