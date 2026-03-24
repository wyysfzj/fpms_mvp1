# Wave 47 Task Plan

## Scope
- Atomic task: `PE-FE-AN-05`
- Task file: `tasks/postenhancement/frontend/PE-FE-AN-05.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/api/govPayments.ts`
  - `frontend/src/api/govPayments.types.ts`
  - `frontend/src/modules/annuity/pages/PayList.vue`
  - `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`

- Atomic task: `PE-FE-CS-01`
- Task file: `tasks/postenhancement/frontend/PE-FE-CS-01.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue`
  - `frontend/src/api/consulting.ts`
  - `frontend/src/api/consulting.types.ts`

- Atomic task: `PE-FE-CS-02`
- Task file: `tasks/postenhancement/frontend/PE-FE-CS-02.md`
- Type: `endpoint page`
- Allowlist:
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`
  - `frontend/src/modules/expenses/pages/ExpenseCreate.vue`
  - `frontend/src/api/expenses.ts`
  - `frontend/src/api/expenses.types.ts`

## Roles
- Architect: freeze contracts for API clients and pages.
- Frontend: implement one atomic task per worker.
- Tester: run gates and FE verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- Each worker must implement exactly one task file only.
- No cross-task file edits.
- All UI text MUST be Simplified Chinese.
