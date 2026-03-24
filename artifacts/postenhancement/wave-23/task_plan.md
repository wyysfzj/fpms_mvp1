# Wave 23 Task Plan

## Scope
- Atomic task: `PE-BE-COM-01`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-01.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`

## Roles
- Architect: freeze create-rule contract.
- Backend: implement `POST /commission/rules` + service validations.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router wiring changes.
- Use existing ORM models only.
- Enforce uniqueness and parameter validation.
