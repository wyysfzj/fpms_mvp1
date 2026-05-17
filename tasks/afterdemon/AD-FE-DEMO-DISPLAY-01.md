# AD-FE-DEMO-DISPLAY-01 — demo-visible frontend display fallback cleanup

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Task Plan Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Normalize demo-visible frontend display fallbacks in the finance lifecycle and shared relation-chain surfaces so user-facing text remains Simplified Chinese and no UUID/raw internal ID is shown when a business-facing label is missing.

This closes only:

1. Shared relation-chain fallback labels for client, case, document, fee draft, and bill links.
2. Fee draft list/detail fallback labels for draft, case, client, and draft type display.
3. Billing create/detail/list/payment/offset fallback labels and option labels for draft, bill, client, payment, payment line, and bill direction display.
4. Shared display text mappings needed by those surfaces for bill status, fee draft type, and bill direction text.

## Explicit Non-Closure

This task does not:

- modify backend code, API wrappers, API payload fields, route params, database schema, or migrations.
- replace remaining raw-ID data entry fields outside the listed demo finance lifecycle surfaces.
- add agent/user selectors, address selectors, applicant selectors, or commission settlement selectors.
- change permissions, menu/router wiring, business state transitions, bill/payment/offset behavior, or response envelopes.
- claim all historical pages in the repository are fully free of internal IDs.

## Remaining Follow-Up Task IDs

- `FE-CASE-FORM-INTERNAL-ID-SELECTORS-01`
- `FE-COMMISSION-USER-CASE-READABLE-DISPLAY-01`
- `FE-TASK-LIST-READABLE-ID-DISPLAY-01`
- `FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DEMO-DISPLAY-01.md`
- `frontend/src/constants/displayText.ts`
- `frontend/src/components/relations/RelationChainCard.vue`
- `frontend/src/modules/fees/pages/FeeDraftList.vue`
- `frontend/src/modules/fees/pages/FeeDraftDetail.vue`
- `frontend/src/modules/billing/pages/BillCreate.vue`
- `frontend/src/modules/billing/pages/BillDetail.vue`
- `frontend/src/modules/billing/pages/BillList.vue`
- `frontend/src/modules/billing/pages/PaymentList.vue`
- `frontend/src/modules/billing/pages/OffsetList.vue`
- `artifacts/AD-FE-DEMO-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DEMO-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/constants/displayText.ts src/components/relations/RelationChainCard.vue src/modules/fees/pages/FeeDraftList.vue src/modules/fees/pages/FeeDraftDetail.vue src/modules/billing/pages/BillCreate.vue src/modules/billing/pages/BillDetail.vue src/modules/billing/pages/BillList.vue src/modules/billing/pages/PaymentList.vue src/modules/billing/pages/OffsetList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DEMO-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DEMO-DISPLAY-01 ux_check /bin/zsh -lc 'rg -n "truncateId|slice\\(0,\\s*8\\)|客户-\\$\\{|案件-\\$\\{|账单-\\$\\{|row\\.bill_id \\|\\||row\\.client_id \\|\\||payment\\.id$|line\\.id \\|" frontend/src/constants/displayText.ts frontend/src/components/relations/RelationChainCard.vue frontend/src/modules/fees/pages/FeeDraftList.vue frontend/src/modules/fees/pages/FeeDraftDetail.vue frontend/src/modules/billing/pages/BillCreate.vue frontend/src/modules/billing/pages/BillDetail.vue frontend/src/modules/billing/pages/BillList.vue frontend/src/modules/billing/pages/PaymentList.vue frontend/src/modules/billing/pages/OffsetList.vue; test $? -eq 1'
./scripts/evidence_run.sh AD-FE-DEMO-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-DEMO-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-DEMO-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-DEMO-DISPLAY-01/summary.md`
- `artifacts/AD-FE-DEMO-DISPLAY-01/git/diff.patch`
