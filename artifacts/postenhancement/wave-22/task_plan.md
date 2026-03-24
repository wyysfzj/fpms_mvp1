# Wave 22 Task Plan

## Scope
- Atomic task: `PE-BE-CL-05`
- Task file: `tasks/postenhancement/backend/PE-BE-CL-05.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`

## Roles
- Architect: freeze bad-debt restore contract.
- Backend: implement `POST /bills/{bill_id}/bad-debt/restore` + restore service logic.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router wiring changes.
- Permission must use parameter injection.
