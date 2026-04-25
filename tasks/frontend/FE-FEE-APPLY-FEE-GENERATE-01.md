# FE-FEE-APPLY-FEE-GENERATE-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Add a user-facing frontend path to generate real `APPLY_FEE` drafts through the
existing backend endpoint and route case fee creation to that path.

This task closes only:

1. Typed frontend API wrapper for `POST /fees/drafts/apply-fee/generate`.
2. Fee draft create page can generate `APPLY_FEE` when requested by query.
3. Case fee tab routes to the real `APPLY_FEE` generation mode.
4. Generated draft details continue to show fee totals and items.

## Explicit Non-Closure

Do not implement pay-list, billing, payment, or commission behavior. Do not
modify backend. Do not modify router/menu permissions.

## Remaining Follow-Up Task IDs

- FE-PAYLIST-FROM-FEE-ITEMS-01

## Allowed Files

- tasks/frontend/FE-FEE-APPLY-FEE-GENERATE-01.md
- frontend/src/api/fees.ts
- frontend/src/api/fees.types.ts
- frontend/src/modules/fees/pages/FeeDraftCreate.vue
- frontend/src/modules/fees/pages/FeeDraftDetail.vue
- frontend/src/modules/cases/components/CaseFeesTab.vue
- artifacts/FE-FEE-APPLY-FEE-GENERATE-01/**

## Verification Commands

```bash
cd frontend && npm run typecheck
cd frontend && npm run build
./scripts/task_validate.sh FE-FEE-APPLY-FEE-GENERATE-01
```

## Evidence Path

- artifacts/FE-FEE-APPLY-FEE-GENERATE-01/results.jsonl
- artifacts/FE-FEE-APPLY-FEE-GENERATE-01/summary.md
- artifacts/FE-FEE-APPLY-FEE-GENERATE-01/git/diff.patch
