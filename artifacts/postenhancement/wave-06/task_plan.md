# Wave 06 Task Plan

## Objective
Continue schema foundation with annuity task table.

## Selected Atomic Task
- `PE-BE-DB-04` — create `T_AnnuityTask`.

## Dependencies
- Depends on prior schema baseline (waves 03-05 complete).

## Assignment
- Architect: contract freeze.
- Backend Developer: task implementation.
- Tester: task gate + migration checks.
- Reviewer: independent sign-off.

## Gates
- `cd backend && alembic upgrade head`
- `./scripts/task_validate.sh PE-BE-DB-04`

## Constraints
- SQLite compatibility.
- allowlist-only edits.
