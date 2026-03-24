# Wave 15 Task Plan

## Objective
Expose batch endpoint for annuity task draft generation.

## Selected Atomic Task
- `PE-BE-AN-05`.

## Assignment
- Architect / Backend / Tester / Reviewer

## Gates
- `cd backend && pytest -q`
- `./scripts/task_validate.sh PE-BE-AN-05`

## Constraints
- allowlist-only edits (`backend/app/modules/annuity/api.py`)
- return batch success/failed details
