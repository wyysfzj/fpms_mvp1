# Wave 13 Task Plan

## Objective
Add annuity client-instruction update endpoint with valid state transitions.

## Selected Atomic Task
- `PE-BE-AN-03`.

## Assignment
- Architect / Backend / Tester / Reviewer

## Gates
- `cd backend && pytest -q`
- `./scripts/task_validate.sh PE-BE-AN-03`

## Constraints
- allowlist-only edits (`backend/app/modules/annuity/api.py`, `backend/app/modules/annuity/service.py`)
- consistent 400/404/409 semantics
