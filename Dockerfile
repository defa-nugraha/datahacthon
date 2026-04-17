FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PROJECT_ROOT=/app \
    API_TITLE="Zone-Based Vegetation Recommendation API" \
    API_VERSION="1.0.0" \
    LOG_LEVEL=INFO

WORKDIR /app

RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --home /app appuser

COPY requirements-api.txt /app/requirements-api.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements-api.txt

COPY app /app/app
COPY scripts /app/scripts
COPY artifacts /app/artifacts
COPY data /app/data
COPY .env.example /app/.env.example
COPY README_FASTAPI.md /app/README_FASTAPI.md

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

