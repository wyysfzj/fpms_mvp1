# Wave 39 Task Plan

## Scope
- Atomic task: `PE-BE-QA-01`
- Task file: `tasks/postenhancement/backend/PE-BE-QA-01.md`
- Type: `service`
- Allowlist:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/billing/api.py`

## Roles
- Architect: freeze error-envelope unification contract.
- Backend: replace naked HTTPException detail with BusinessError envelope pattern.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
- Keep endpoint response contracts unchanged; only error envelope consistency.
