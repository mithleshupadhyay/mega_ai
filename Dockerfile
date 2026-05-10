FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.2

COPY pyproject.toml poetry.lock* README.md ./
COPY src ./src
RUN poetry config virtualenvs.create false \
    && poetry install --with dev --no-interaction --no-ansi

COPY . .

CMD ["uvicorn", "mega_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
