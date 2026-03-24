# Wave 38 Task Plan

## Scope
- Atomic task: `PE-BE-CS-06`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-06.md`
- Type: `service`
- Allowlist:
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/billing/service.py`

## Roles
- Architect: freeze consulting commission integration contract.
- Backend: implement commission-rule integration on consulting bill generation path.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
