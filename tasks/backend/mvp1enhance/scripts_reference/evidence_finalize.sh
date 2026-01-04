#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
if [[ -z "$TASK_ID" ]]; then
  echo "Usage: scripts/evidence_finalize.sh <TASK-ID>"
  exit 2
fi

ART_DIR="artifacts/${TASK_ID}"
GIT_DIR="${ART_DIR}/git"
ENV_DIR="${ART_DIR}/env"
mkdir -p "${GIT_DIR}" "${ENV_DIR}"

git rev-parse HEAD > "${GIT_DIR}/rev.txt" 2>/dev/null || true
git status --porcelain=v1 > "${GIT_DIR}/status.txt" 2>/dev/null || true
git diff > "${GIT_DIR}/diff.patch" 2>/dev/null || true

uname -a > "${ENV_DIR}/uname.txt" 2>/dev/null || true
( python3 --version 2>/dev/null || true ) > "${ENV_DIR}/python3_version.txt" 2>&1 || true

SUM="${ART_DIR}/summary.md"
if [[ ! -f "${SUM}" ]]; then
cat > "${SUM}" <<'MD'
# Task Summary

- TASK-ID:
- Short description:
- Status: DONE

## Change Summary
- 

## Files Changed
- 

## Verification (Evidence)
- Lint: ✅ (log: artifacts/<TASK-ID>/outputs/...)
- Test: ✅
- E2E/Contract: ✅ / N/A

## Risks / Rollback
- 

## Evidence Pack
- artifacts/<TASK-ID>/
  - commands.jsonl
  - results.jsonl
  - outputs/
  - git/diff.patch
MD
fi

echo "Evidence finalized at: ${ART_DIR}"
