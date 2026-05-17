#!/usr/bin/env bash
set -euo pipefail

mkdir -p /data/storage

cd /app/backend

echo "Running database migrations..."
alembic upgrade head

if [[ "${FPMS_RUN_SEED:-1}" != "0" ]]; then
  echo "Running idempotent demo seed..."
  python scripts/seed_dev.py
else
  echo "Skipping demo seed because FPMS_RUN_SEED=0"
fi

uvicorn app.main:app --host 127.0.0.1 --port "${FPMS_API_PORT:-8000}" &
api_pid=$!

nginx -g "daemon off;" &
nginx_pid=$!

shutdown() {
  kill -TERM "$api_pid" "$nginx_pid" 2>/dev/null || true
  wait "$api_pid" "$nginx_pid" 2>/dev/null || true
}

trap shutdown SIGINT SIGTERM

set +e
wait -n "$api_pid" "$nginx_pid"
exit_code=$?
set -e

shutdown
exit "$exit_code"
