FROM python:3.12-slim

RUN apt-get update && apt-get install -y gcc libffi-dev build-essential


RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

COPY . /app