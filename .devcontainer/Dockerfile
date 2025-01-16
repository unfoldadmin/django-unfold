FROM mcr.microsoft.com/devcontainers/python:3.13

ENV PYTHONUNBUFFERED 1

RUN pip install poetry==1.8

RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /app/

WORKDIR /app

RUN poetry install --no-root

EXPOSE 8000
