FROM python:3.11-slim

ARG MODEL_ID
ENV MODEL_ID $MODEL_ID

RUN pip install poetry==1.8.3

RUN poetry config virtualenvs.create false

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry install --without dev --no-interaction --no-ansi --no-root

COPY ./app.py ./

ADD ./artifacts/models/${MODEL_ID} ./

EXPOSE 8080

CMD exec uvicorn app:app --host 0.0.0.0 --port 8080

