#!/usr/bin/env bash
set -euo pipefail
FILE="${1:-}"
if [[ -z "$FILE" ]]; then
  echo "Usage: $0 <python_file_relative_to_backend>"
  exit 1
fi
cd backend
echo "[1/3] ruff check"
ruff check .
echo "[2/3] python compile"
python -m py_compile "$FILE"
echo "[3/3] pytest (optional; may be slow)"
pytest -q || true
echo "Done."
