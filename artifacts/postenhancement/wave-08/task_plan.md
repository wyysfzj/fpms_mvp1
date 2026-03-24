# Wave 08 Task Plan

## Objective
Create commission rule schema foundation.

## Selected Atomic Task
- `PE-BE-DB-06`.

## Assignment
- Architect: freeze
- Backend: implement
- Tester: validate
- Reviewer: sign-off

## Gates
- `cd backend && alembic upgrade head`
- `./scripts/task_validate.sh PE-BE-DB-06`

## Constraints
- SQLite compatibility
- allowlist-only edits
