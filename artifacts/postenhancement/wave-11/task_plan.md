# Wave 11 Task Plan

## Objective
Implement annuity task query service with due-range/status filtering.

## Selected Atomic Task
- `PE-BE-AN-01`.

## Assignment
- Architect / Backend / Tester / Reviewer

## Gates
- `cd backend && pytest -q tests/test_b6_search_filters.py`
- `./scripts/task_validate.sh PE-BE-AN-01`

## Constraints
- allowlist-only edits
- keep pagination behavior deterministic
