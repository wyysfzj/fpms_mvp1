# Wave 18 Task Plan

## Scope
- Atomic task: `PE-BE-CL-01`
- Task file: `tasks/postenhancement/backend/PE-BE-CL-01.md`
- Type: `service`
- Allowlist:
  - `backend/app/modules/collections/service.py`

## Roles
- Architect: freeze contract and acceptance checklist.
- Backend: implement overdue bill filtering + dunning batch generation service.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No schema/migration/router changes.
- Preserve existing error semantics and response envelope conventions.
