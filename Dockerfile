
FROM python:3.9-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN groupadd -r flutterwave && useradd -r -g flutterwave agentuser

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY src/ ./src/
COPY gunicorn_conf.py .

RUN mkdir -p /app/huggingface_cache && \
    chown -R agentuser:flutterwave /app

USER agentuser

ENV TRANSFORMERS_CACHE=/app/huggingface_cache \
    HF_HOME=/app/huggingface_cache

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn_conf.py", "src.server:app"]
