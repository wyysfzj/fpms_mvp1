# Wave 17 Task Plan

## Objective
Implement official government payment registration endpoint.

## Selected Atomic Task
- `PE-BE-AN-07`.

## Assignment
- Architect / Backend / Tester / Reviewer

## Gates
- `cd backend && pytest -q`
- `./scripts/task_validate.sh PE-BE-AN-07`

## Constraints
- allowlist-only edits (`backend/app/modules/annuity/api.py`, `backend/app/modules/annuity/service.py`)
- support duplicate protection and pay-list status update
