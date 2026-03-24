# Wave 35 Task Plan

## Scope
- Atomic task: `PE-BE-CS-03`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-03.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`

## Roles
- Architect: freeze expense query/stats contract.
- Backend: implement `GET /expenses` query + summary stats.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
- Permission injection required (`Expense.Read`).
