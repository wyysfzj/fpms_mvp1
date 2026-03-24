# Wave 12 Task Plan

## Objective
Expose annuity task query endpoint.

## Selected Atomic Task
- `PE-BE-AN-02`.

## Assignment
- Architect / Backend / Tester / Reviewer

## Gates
- `cd backend && ruff check . && pytest -q`
- `./scripts/task_validate.sh PE-BE-AN-02`

## Constraints
- allowlist-only edits (`backend/app/modules/annuity/api.py`)
- preserve permission and envelope conventions
