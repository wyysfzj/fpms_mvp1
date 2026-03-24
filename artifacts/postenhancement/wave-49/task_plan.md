# Wave 49 Task Plan

## Scope
- Atomic task: `PE-FE-QA-01`
- Task file: `tasks/postenhancement/frontend/PE-FE-QA-01.md`
- Type: `service`
- Allowlist:
  - `frontend/src/router/index.ts`
  - `frontend/src/constants/menu.ts`

## Roles
- Architect: freeze route/menu/permission gate integration contract.
- Frontend: implement one atomic task.
- Tester: run task gate + frontend verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- No regression for existing old menus/routes behavior.
- All UI text MUST be Simplified Chinese.
