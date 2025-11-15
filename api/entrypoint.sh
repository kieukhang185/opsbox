#!/bin/bash

# Wait for Postgres to be ready
echo "Waiting for postgres..."

# Try up to 30 times (30 seconds)
for i in $(seq 1 30); do
  nc -z postgres 5432 && break
  echo "Postgres not ready yet... ($i)"
  sleep 1
done

nc -z postgres 5432
if [[ $? -ne 0 ]]; then
  echo "Postgres not reachable after 30 seconds, giving up."
  exit 1
fi

echo "Postgres is up - starting FastAPI"

# Run migrations or create tables here if you wish (optional)
# python app/init_db.py

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
