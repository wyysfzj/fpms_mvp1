# Wave 31 Task Plan

## Scope
- Atomic task: `PE-BE-COM-09`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-09.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`

## Roles
- Architect: freeze settlement line generation contract.
- Backend: implement `POST /commission/settlements/{id}/generate-lines`.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
- Deterministic selection and idempotent line generation.
