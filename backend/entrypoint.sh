#!/bin/sh

set -e

echo "🚀 Starting backend..."

# -----------------------
# WAIT FOR POSTGRES (DEV + PROD ONLY)
# -----------------------
echo "⏳ Waiting for Postgres..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
  echo "Postgres not ready..."
  sleep 2
done

echo "✅ Postgres is ready"

# -----------------------
# RUN MIGRATIONS
# -----------------------
echo "🧬 Running Alembic migrations..."

alembic upgrade head

echo "✅ Migrations complete"

# -----------------------
# START SERVER
# -----------------------
if [ "$ENV" = "production" ]; then
    echo "🚀 Running in production mode"

    exec gunicorn app.main:app \
        -k uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --workers ${WORKERS:-1}   # safe default
else
    echo "🛠 Running in development mode"

    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
fi
