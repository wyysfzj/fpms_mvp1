# Wave 25 Task Plan

## Scope
- Atomic task: `PE-BE-COM-03`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-03.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`

## Roles
- Architect: freeze update-rule contract.
- Backend: implement `PUT /commission/rules/{rule_id}` safely.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router wiring changes.
- Preserve uniqueness and validation guarantees.
