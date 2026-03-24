# Wave 05 Task Plan

## Objective
Continue schema foundation with government payment detail table.

## Selected Atomic Task
- `PE-BE-DB-03` — create `T_GovPayment`.

## Dependencies
- Depends on `PE-BE-DB-02` (completed).

## Assignment
- Architect: contract freeze.
- Backend Developer: task implementation.
- Tester: task gate + migration checks.
- Reviewer: independent sign-off.

## Gates
- `cd backend && alembic upgrade head`
- `./scripts/task_validate.sh PE-BE-DB-03`

## Constraints
- SQLite compatibility.
- allowlist-only edits.
