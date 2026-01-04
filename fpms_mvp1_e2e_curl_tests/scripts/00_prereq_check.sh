#!/usr/bin/env bash
set -euo pipefail
source scripts/_common.sh
need_cmd curl
need_cmd jq
echo "OK: curl and jq found"
echo "BASE_URL=${BASE_URL}"
echo "API_PREFIX=${API_PREFIX}"
echo "Token present (not displayed)"
