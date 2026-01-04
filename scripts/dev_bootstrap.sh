#!/usr/bin/env bash
set -euo pipefail

echo "[1/3] Backend venv + deps"
cd backend
python -m venv .venv || true
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
cp -n .env.example .env || true

echo "[2/3] DB migrate (SQLite)"
alembic upgrade head || true

echo "[3/3] Frontend deps"
cd ../frontend
npm i
cp -n .env.example .env || true

echo "Done. Run:"
echo "  make dev-backend"
echo "  make dev-frontend"
