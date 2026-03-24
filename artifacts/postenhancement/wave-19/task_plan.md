# Wave 19 Task Plan

## Scope
- Atomic task: `PE-BE-CL-02`
- Task file: `tasks/postenhancement/backend/PE-BE-CL-02.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/collections/api.py`

## Roles
- Architect: freeze endpoint contract and acceptance checklist.
- Backend: implement `POST /dunning` API using existing collections service.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router wiring changes.
- Permission must use parameter injection (`Depends(require_perm("Dunning.Create"))`).
- Preserve existing error envelope conventions.
