# Wave 37 Task Plan

## Scope
- Atomic task: `PE-BE-CS-05`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-05.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`

## Roles
- Architect: freeze consulting fee-draft API contract.
- Backend: implement `POST /consulting/fee-drafts`.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
