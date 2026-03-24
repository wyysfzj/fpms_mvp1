# Wave 07 Task Plan

## Objective
Create collections schema foundation (`T_Dunning`, `T_DunningLine`).

## Selected Atomic Task
- `PE-BE-DB-05`.

## Assignment
- Architect: freeze
- Backend: implement
- Tester: validate
- Reviewer: sign-off

## Gates
- `cd backend && alembic upgrade head`
- `./scripts/task_validate.sh PE-BE-DB-05`

## Constraints
- SQLite compatibility
- allowlist-only edits
