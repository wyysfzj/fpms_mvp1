# Wave 43 Task Plan

## Scope
- Atomic task: `PE-FE-AN-01`
- Task file: `tasks/postenhancement/frontend/PE-FE-AN-01.md`
- Type: `service`
- Allowlist:
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`

- Atomic task: `PE-FE-CL-01`
- Task file: `tasks/postenhancement/frontend/PE-FE-CL-01.md`
- Type: `service`
- Allowlist:
  - `frontend/src/api/collections.ts`
  - `frontend/src/api/collections.types.ts`

- Atomic task: `PE-FE-COM-01`
- Task file: `tasks/postenhancement/frontend/PE-FE-COM-01.md`
- Type: `service`
- Allowlist:
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`

## Roles
- Architect: freeze API contract and coding conventions for 3 FE API clients.
- Frontend: implement one atomic task per worker.
- Tester: run task gates and frontend verification (`lint` + `typecheck` + `build`).
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- Each worker must implement exactly one task file only.
- No cross-task file edits.
- Frontend iron rule remains mandatory for user-facing text: Simplified Chinese only.
