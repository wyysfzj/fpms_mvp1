#!/usr/bin/env bash
set -euo pipefail

shopt -s nullglob

MANIFEST=""
EXCLUDE_TASK=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --manifest)
      [ "$#" -ge 2 ] || { echo "Missing value for --manifest"; exit 2; }
      MANIFEST=$2
      shift 2
      ;;
    --exclude-task)
      [ "$#" -ge 2 ] || { echo "Missing value for --exclude-task"; exit 2; }
      EXCLUDE_TASK=$2
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 2
      ;;
  esac
done

TASK_IDS=()

if [ -n "$MANIFEST" ]; then
  [ -f "$MANIFEST" ] || { echo "Manifest not found: $MANIFEST"; exit 2; }
  DECLARED_COUNT=$(grep -c '^- Task file:' "$MANIFEST" || true)
  PARSED_COUNT=0
  SELECTED_COUNT=0
  EXCLUDE_FOUND=0
  SEEN_TASKS="|"
  while IFS= read -r task_id; do
    PARSED_COUNT=$((PARSED_COUNT + 1))
    case "$task_id" in
      *[!A-Za-z0-9._-]*|"")
        echo "Invalid task ID in manifest: $task_id"
        exit 2
        ;;
    esac
    case "$SEEN_TASKS" in
      *"|$task_id|"*)
        echo "Duplicate task ID in manifest: $task_id"
        exit 2
        ;;
    esac
    SEEN_TASKS="${SEEN_TASKS}${task_id}|"
    if [ "$task_id" != "$EXCLUDE_TASK" ]; then
      TASK_IDS+=("$task_id")
      SELECTED_COUNT=$((SELECTED_COUNT + 1))
    else
      EXCLUDE_FOUND=1
    fi
  done < <(
    sed -n \
      -e 's|^- Task file: `tasks/additional_gaps/\([^/`]*\)\.md`$|\1|p' \
      -e 's|^- Task file: `tasks/postdemo/v8/\([^/`]*\)\.md`$|\1|p' \
      "$MANIFEST"
  )
  if [ "$DECLARED_COUNT" -ne "$PARSED_COUNT" ]; then
    echo "Manifest contains an invalid task-file declaration"
    exit 2
  fi
  [ "$PARSED_COUNT" -gt 0 ] || { echo "Manifest contains no task entries"; exit 2; }
  if [ -n "$EXCLUDE_TASK" ] && [ "$EXCLUDE_FOUND" -ne 1 ]; then
    echo "Excluded task is not listed in manifest: $EXCLUDE_TASK"
    exit 2
  fi
  [ "$SELECTED_COUNT" -gt 0 ] || { echo "No tasks selected from manifest"; exit 2; }
else
  [ -z "$EXCLUDE_TASK" ] || { echo "--exclude-task requires --manifest"; exit 2; }
  ART_DIRS=(artifacts/ENH-*)
  if [ "${#ART_DIRS[@]}" -eq 0 ]; then
    echo "No task artifacts found"
    exit 1
  fi
  for dir in "${ART_DIRS[@]}"; do
    TASK_IDS+=("${dir#artifacts/}")
  done
fi

PASS=0
FAIL=0

for TASK_ID in "${TASK_IDS[@]}"; do
  if ./scripts/task_validate.sh "$TASK_ID"; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
  fi
done

echo "Release Gate: $PASS passed, $FAIL failed"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
