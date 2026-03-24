# Wave 34 Task Plan

## Scope
- Atomic task: `PE-BE-CS-02`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-02.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`

## Roles
- Architect: freeze expense create contract.
- Backend: implement `POST /expenses` with validation.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
