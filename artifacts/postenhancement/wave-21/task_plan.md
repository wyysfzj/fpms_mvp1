# Wave 21 Task Plan

## Scope
- Atomic task: `PE-BE-CL-04`
- Task file: `tasks/postenhancement/backend/PE-BE-CL-04.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`

## Roles
- Architect: freeze bad-debt mark contract.
- Backend: implement `POST /bills/{bill_id}/bad-debt` + service rules.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router wiring changes.
- Permission must use parameter injection.
- Only bills with outstanding balance can be marked bad debt.
