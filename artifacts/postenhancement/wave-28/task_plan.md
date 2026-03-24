# Wave 28 Task Plan

## Scope
- Atomic task: `PE-BE-COM-06`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-06.md`
- Type: `service`
- Allowlist:
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`

## Roles
- Architect: freeze settleable recompute contract.
- Backend: implement WaitPay/ForceSettle recompute and wire on offset/reverse.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
- Keep billing response contract unchanged.
