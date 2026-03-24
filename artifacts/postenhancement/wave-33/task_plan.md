# Wave 33 Task Plan

## Scope
- Atomic task: `PE-BE-CS-01`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-01.md`
- Type: `endpoint`
- Allowlist:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/cases/service.py`

## Roles
- Architect: freeze consulting/search case creation contract.
- Backend: implement `POST /consulting/cases` and required validation branches.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
- Keep existing `/cases` behavior stable.
