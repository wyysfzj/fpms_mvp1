# Wave 16 Task Plan

## Objective
Implement pay-list generation endpoint from fee items.

## Selected Atomic Task
- `PE-BE-AN-06`.

## Assignment
- Architect / Backend / Tester / Reviewer

## Gates
- `cd backend && pytest -q`
- `./scripts/task_validate.sh PE-BE-AN-06`

## Constraints
- allowlist-only edits (`backend/app/modules/annuity/api.py`, `backend/app/modules/annuity/service.py`)
- enforce same client/currency constraints
