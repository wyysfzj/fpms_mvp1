# Wave 01 Task Plan

## Objective
Execute first low-coupling post-enhancement tasks with 6-role team workflow.

## Selected Atomic Tasks
- Backend:
  - `PE-BE-00-01` — extend CaseType enum for `CONSULTING`/`SEARCH`.
  - `PE-BE-00-03` — add error semantics/envelope guidance for new domains.
- Frontend:
  - `PE-FE-00-01` — align permission constants to `Title.Action` naming.
  - `PE-FE-00-03` — frontend error/status handling doc update.

## Dependency Graph
- `PE-BE-00-01`: none
- `PE-BE-00-03`: none
- `PE-FE-00-01`: none
- `PE-FE-00-03`: none

## Team Assignment
- Architect (`explorer`): contract freeze + boundary checks.
- Backend Dev (`worker`): `PE-BE-00-01` + `PE-BE-00-03` as two separate executions.
- Frontend Dev (`worker`): `PE-FE-00-01` + `PE-FE-00-03` as two separate executions.
- Tester (`worker`): run gates and collect evidence.
- Reviewer (`explorer`): independent acceptance review.
- Lead (main thread): coordination and progress tracking.

## Gates
- Backend: `cd backend && ruff check . && pytest -q`
- Frontend: `cd frontend && npm run lint && npm run typecheck`

## Non-Regression Constraints
- Strict allowlist per task file.
- No cross-scope edits.
- Preserve existing functionality.
