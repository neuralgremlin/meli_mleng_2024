FROM python:3.11-slim

RUN pip install poetry==1.8.3

RUN poetry config virtualenvs.create false

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./main.py ./

EXPOSE 8080

CMD exec uvicorn main:app --host 0.0.0.0 --port 8080


