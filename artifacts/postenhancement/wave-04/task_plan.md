# Wave 04 Task Plan

## Objective
Continue schema foundation with PayList header table.

## Selected Atomic Task
- `PE-BE-DB-02` — create `T_PayList`.

## Dependencies
- Depends on `PE-BE-DB-01` (completed).

## Assignment
- Architect: contract freeze.
- Backend Developer: task implementation.
- Tester: task gate + migration checks.
- Reviewer: independent sign-off.

## Gates
- `cd backend && alembic upgrade head`
- `./scripts/task_validate.sh PE-BE-DB-02`

## Constraints
- SQLite compatibility.
- allowlist-only edits.
