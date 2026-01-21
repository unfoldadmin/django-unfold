FROM mcr.microsoft.com/devcontainers/python:3.14

ENV PYTHONUNBUFFERED 1

ENV UV_PROJECT_ENVIRONMENT=/.venv

RUN pip install uv

COPY pyproject.toml uv.lock README.md  /app/

WORKDIR /app

RUN uv sync

EXPOSE 8000
