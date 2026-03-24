# Wave 45 Task Plan

## Scope
- Atomic task: `PE-FE-AN-03`
- Task file: `tasks/postenhancement/frontend/PE-FE-AN-03.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/annuity/components/InstructionDialog.vue`
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`

- Atomic task: `PE-FE-CL-03`
- Task file: `tasks/postenhancement/frontend/PE-FE-CL-03.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/collections/pages/DunningList.vue`
  - `frontend/src/modules/collections/pages/DunningDetail.vue`

- Atomic task: `PE-FE-COM-03`
- Task file: `tasks/postenhancement/frontend/PE-FE-COM-03.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionList.vue`

## Roles
- Architect: freeze UI interactions, data contract, and error handling for 3 pages.
- Frontend: implement one atomic task per worker.
- Tester: run task gates and FE verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- Each worker must implement exactly one task file only.
- No cross-task file edits.
- All UI text MUST be Simplified Chinese.
