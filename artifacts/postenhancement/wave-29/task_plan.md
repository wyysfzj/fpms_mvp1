# Wave 29 Task Plan

## Scope
- Atomic task: `PE-BE-COM-07`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-07.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/commission/api.py`

## Roles
- Architect: freeze commission list contract.
- Backend: implement `GET /commission` with required filters.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
- Permission injection required.
