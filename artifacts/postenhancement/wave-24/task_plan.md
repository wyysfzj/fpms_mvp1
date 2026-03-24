# Wave 24 Task Plan

## Scope
- Atomic task: `PE-BE-COM-02`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-02.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/commission/api.py`

## Roles
- Architect: freeze list rules contract.
- Backend: implement `GET /commission/rules` with filter + pagination.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router wiring changes.
- Permission must use parameter injection (`CommissionRule.Read`).
