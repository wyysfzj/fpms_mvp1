#!/usr/bin/env bash
set -euo pipefail
cd frontend
echo "[1/2] typecheck/build"
npm run build
echo "[2/2] dev server (manual check)"
echo "Run: npm run dev"
