# Wave 32 Task Plan

## Scope
- Atomic task: `PE-BE-COM-10`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-10.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`

## Roles
- Architect: freeze settlement report contract.
- Backend: implement `GET /commission/reports/settlement` aggregation.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
