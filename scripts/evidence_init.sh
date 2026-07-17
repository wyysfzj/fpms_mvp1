#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: ./scripts/evidence_init.sh <TASK-ID> --task-file <path> [--allowlist <path>...]"
  exit 2
}

[ "$#" -ge 3 ] || usage

TASK_ID=$1
shift
TASK_FILE=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --task-file)
      [ "$#" -ge 2 ] || usage
      [ -z "$TASK_FILE" ] || usage
      TASK_FILE=$2
      shift 2
      ;;
    --allowlist)
      shift
      [ "$#" -ge 1 ] || usage
      case "$1" in
        --*) usage ;;
      esac
      while [ "$#" -gt 0 ]; do
        case "$1" in
          --*) break ;;
          *) shift ;;
        esac
      done
      ;;
    *) usage ;;
  esac
done

[ -n "$TASK_FILE" ] || usage

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$SCRIPT_DIR/taskctl" "$TASK_ID" start --task-file "$TASK_FILE"
