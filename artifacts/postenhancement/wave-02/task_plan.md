# Wave 02 Task Plan

## Objective
Implement permission synchronization baseline after Wave 01.

## Selected Atomic Tasks
- Backend:
  - `PE-BE-00-02` — add new-domain permission constants into RBAC seed and permissions matrix.
- Frontend:
  - `PE-FE-00-02` — fetch real permissions post-login and persist into auth store (secure default, non-permissive unknown).

## Dependency Graph
- `PE-BE-00-02` depends on `PE-BE-00-01` (completed in Wave 01).
- `PE-FE-00-02` depends on `PE-FE-00-01` (completed in Wave 01).

## Team Assignment
- Architect (`explorer`): contract freeze and compatibility checks.
- Backend Dev (`worker`): `PE-BE-00-02`.
- Frontend Dev (`worker`): `PE-FE-00-02`.
- Tester (`worker`): gates + allowlist/evidence checks.
- Reviewer (`explorer`): independent review and sign-off.

## Gates
- Backend: `cd backend && pytest -q tests/test_system_params.py`
- Frontend: `cd frontend && npm run lint && npm run typecheck`
- Task gate: `./scripts/task_validate.sh <TASK-ID>`

## Non-Regression Constraints
- Strict allowlist per task file.
- Keep permission codes aligned to `Title.Action`.
- No API contract break for existing flows.
