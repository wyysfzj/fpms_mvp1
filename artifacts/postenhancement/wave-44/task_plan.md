# Wave 44 Task Plan

## Scope
- Atomic task: `PE-FE-AN-02`
- Task file: `tasks/postenhancement/frontend/PE-FE-AN-02.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
  - `frontend/src/router/index.ts`

- Atomic task: `PE-FE-CL-02`
- Task file: `tasks/postenhancement/frontend/PE-FE-CL-02.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/collections/pages/DunningCreate.vue`

- Atomic task: `PE-FE-COM-02`
- Task file: `tasks/postenhancement/frontend/PE-FE-COM-02.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionRuleList.vue`

## Roles
- Architect: freeze UI page contract, interaction behavior, and API binding rules.
- Frontend: implement one atomic task per worker.
- Tester: run task gates and FE verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- Each worker must implement exactly one task file only.
- No cross-task file edits.
- All UI text MUST be Simplified Chinese.
