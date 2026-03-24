# Wave 20 Task Plan

## Scope
- Atomic task: `PE-BE-CL-03`
- Task file: `tasks/postenhancement/backend/PE-BE-CL-03.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/collections/api.py`

## Roles
- Architect: freeze query/filter/pagination contract.
- Backend: implement `GET /dunning` with round/status/client filters and pagination.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router wiring changes.
- Permission must use parameter injection (`Depends(require_perm("Dunning.Read"))`).
- Keep response envelope consistent with module conventions.
