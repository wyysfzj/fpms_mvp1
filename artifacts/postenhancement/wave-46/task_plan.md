# Wave 46 Task Plan

## Scope
- Atomic task: `PE-FE-AN-04`
- Task file: `tasks/postenhancement/frontend/PE-FE-AN-04.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`

- Atomic task: `PE-FE-CL-04`
- Task file: `tasks/postenhancement/frontend/PE-FE-CL-04.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/billing/pages/BillDetail.vue`

- Atomic task: `PE-FE-COM-04`
- Task file: `tasks/postenhancement/frontend/PE-FE-COM-04.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`

## Roles
- Architect: freeze UI behavior and API contracts.
- Frontend: implement one atomic task per worker.
- Tester: run task gates and FE verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- Each worker must implement exactly one task file only.
- No cross-task file edits.
- All UI text MUST be Simplified Chinese.
