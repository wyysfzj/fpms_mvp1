# Wave 26 Task Plan

## Scope
- Atomic task: `PE-BE-COM-04`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-04.md`
- Type: `service`
- Allowlist:
  - `backend/app/modules/commission/service.py`

## Roles
- Architect: freeze commission generation service contract.
- Backend: implement bill-triggered commission generate/update service.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
- Use existing models only.
- Keep service deterministic and idempotent-safe for same bill input.
