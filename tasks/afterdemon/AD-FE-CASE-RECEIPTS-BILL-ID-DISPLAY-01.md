# AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01 - case receipts visible bill ID cleanup

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Remove visible raw bill UUID/code displays from the case detail `账单与收款` summary component.

This closes only:

1. `CaseReceiptsSummary.vue` related-bill rows no longer render UUID-shaped `bill_no` values as user-visible text.
2. `CaseReceiptsSummary.vue` uses existing readable bill data when available and otherwise shows minimal Chinese business fallbacks (`已关联账单` / `未生成账单号`).
3. `CaseReceiptsSummary.vue` displays the enriched receipt fee type as a Chinese label instead of raw fee-type code text.

## Explicit Non-Closure

This task does not:

- modify backend code, billing API wrappers/types, case detail tab wiring, route params, permissions, response envelopes, or fetch behavior.
- change bill/payment/receipt creation, offset, row click routing, amount calculation, status calculation, pagination, export, or print behavior.
- add bill-number generation, bill-name resolution, or any new API join.
- close billing display issues outside `CaseReceiptsSummary.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`
- `AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01.md`
- `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`
- `artifacts/AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/cases/components/CaseReceiptsSummary.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "\\{\\{ row\\.bill_no \\}\\}|\\{\\{ receipts\\.fee_type \\}\\}|return map\\[type\\] \\|\\| type" frontend/src/modules/cases/components/CaseReceiptsSummary.vue && rg -n "formatBillDisplay|formatFeeTypeDisplay|已关联账单|未生成账单号|未知费用类型" frontend/src/modules/cases/components/CaseReceiptsSummary.vue'
./scripts/evidence_run.sh AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CASE-RECEIPTS-BILL-ID-DISPLAY-01/baseline_external_files.txt`
