# Wave 30 Task Plan

## Scope
- Atomic task: `PE-BE-COM-08`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-08.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`

## Roles
- Architect: freeze create-settlement contract.
- Backend: implement `POST /commission/settlements`.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
- Validate uniqueness and state conventions.
