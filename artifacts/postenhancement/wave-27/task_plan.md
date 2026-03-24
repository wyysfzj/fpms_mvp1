# Wave 27 Task Plan

## Scope
- Atomic task: `PE-BE-COM-05`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-05.md`
- Type: `service`
- Allowlist:
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/commission/service.py`

## Roles
- Architect: freeze billing hook contract.
- Backend: wire commission service into billing generation path with non-blocking strategy.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
- Existing billing API return contracts must not change.
