FROM python:3.12-slim

# Install system dependencies + Postgres client
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy dependencies first (cache optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY entrypoint.sh .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Expose FastAPI port
EXPOSE 8000

# Start container
CMD ["/app/entrypoint.sh"]
