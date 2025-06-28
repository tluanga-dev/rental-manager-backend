#!/bin/bash

echo "Waiting for database to be ready..."
while ! pg_isready -h db -p 5432 -U rental_user; do
  sleep 1
done

echo "Database is ready. Running migrations..."
alembic upgrade head

echo "Starting FastAPI application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload