#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: ./scripts/task_validate.sh <TASK-ID>"
  exit 2
fi

TASK_ID=$1
ART_DIR="artifacts/$TASK_ID"

[ -d "$ART_DIR" ] || { echo "Missing artifacts"; exit 1; }
[ -f "$ART_DIR/summary.md" ] || { echo "Missing summary"; exit 1; }
[ -f "$ART_DIR/results.jsonl" ] || { echo "Missing results"; exit 1; }
[ -f "$ART_DIR/git/diff.patch" ] || { echo "Missing git diff"; exit 1; }

grep -q '"step":"lint".*"rc":0' "$ART_DIR/results.jsonl" || exit 1
grep -q '"step":"test".*"rc":0' "$ART_DIR/results.jsonl" || exit 1

echo "Task Gate PASS"
