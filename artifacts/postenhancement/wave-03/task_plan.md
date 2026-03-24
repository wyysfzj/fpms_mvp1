# Wave 03 Task Plan

## Objective
Start schema foundation for post-enhancement business domains.

## Selected Atomic Tasks
- Backend:
  - `PE-BE-DB-01` — create `T_Expense` schema/model.

## Dependency Graph
- `PE-BE-DB-01` depends on `PE-BE-00-01` (completed).

## Team Assignment
- Architect (`explorer`): schema/SQLite compatibility freeze.
- Backend Dev (`worker`): implement `PE-BE-DB-01`.
- Tester (`worker`): migration + compile validation and task gate.
- Reviewer (`explorer`): independent review and sign-off.
- Frontend role: standby (no unblocked FE tasks before backend domain APIs).

## Gates
- `cd backend && alembic upgrade head`
- `cd backend && python3 -m py_compile app/modules/expenses/models.py`
- `./scripts/task_validate.sh PE-BE-DB-01`

## Constraints
- SQLite compatibility required.
- No unrelated migrations or refactors.
- Allowlist strictness.
