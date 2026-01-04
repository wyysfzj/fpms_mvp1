#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: ./scripts/evidence_finalize.sh <TASK-ID>"
  exit 2
fi

TASK_ID=$1
ART_DIR="artifacts/$TASK_ID"
GIT_DIR="$ART_DIR/git"

mkdir -p "$GIT_DIR"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git diff >"$GIT_DIR/diff.patch"
  git status -sb >"$GIT_DIR/status.txt"
  git rev-parse HEAD >"$GIT_DIR/rev.txt"
else
  echo "Not a git repository" >"$GIT_DIR/diff.patch"
  echo "Not a git repository" >"$GIT_DIR/status.txt"
  echo "unknown" >"$GIT_DIR/rev.txt"
fi

SUMMARY_PATH="$ART_DIR/summary.md"
if [ ! -f "$SUMMARY_PATH" ]; then
  cat <<'SUMMARY' >"$SUMMARY_PATH"
# Summary

## Commands
- 

## Results
- 

## Notes
- 
SUMMARY
fi
