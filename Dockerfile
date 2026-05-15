FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml ./
COPY usj_http ./usj_http

RUN mkdir -p /app/logs

EXPOSE 8080

CMD ["python", "-m", "usj_http.server", "--host", "0.0.0.0", "--port", "8080", "--log-file", "/app/logs/server.log"]
