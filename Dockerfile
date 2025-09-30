FROM python:3.12-alpine
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn asyncpg pydantic python-dotenv
COPY src/ ./app/
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}", "--workers ${MAX_WORKERS}"]