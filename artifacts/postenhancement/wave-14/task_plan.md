# Wave 14 Task Plan

## Objective
Implement annuity-task to fee-draft generation service with idempotence.

## Selected Atomic Task
- `PE-BE-AN-04`.

## Assignment
- Architect / Backend / Tester / Reviewer

## Gates
- `cd backend && pytest -q`
- `./scripts/task_validate.sh PE-BE-AN-04`

## Constraints
- allowlist-only edits (`backend/app/modules/annuity/service.py`)
- enforce idempotence and PayNextYear option
