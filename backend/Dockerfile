FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# CMD ["uvicorn", "app_main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["sh", "-c", "uvicorn app_main:app --host 0.0.0.0 --port ${PORT:-8080}"]

# FROM python:3.11-slim

# # Install system deps
# RUN apt-get update && apt-get install -y gcc g++ libpq-dev curl && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# # Upgrade pip and install requirements
# COPY requirements.txt .
# RUN pip install --upgrade pip \
#     && pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY . .

# # Create non-root user
# RUN useradd --create-home appuser && chown -R appuser:appuser /app
# USER appuser

# # Listen on port Cloud Run expects
# EXPOSE 8080

# # Start Uvicorn on $PORT (default 8080)
# CMD ["sh", "-c", "uvicorn app_main:app --host 0.0.0.0 --port ${PORT:-8080}"]