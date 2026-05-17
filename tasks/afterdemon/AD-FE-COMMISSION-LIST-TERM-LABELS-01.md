# AD-FE-COMMISSION-LIST-TERM-LABELS-01 - commission list visible term and enum cleanup

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

Normalize user-visible terminology and enum labels on the commission record list page.

This closes only:

1. `CommissionList.vue` uses the product term `案号` instead of `案卷号` for the case-number filter placeholder and table header.
2. `CommissionList.vue` renders visible fee-type values as Simplified Chinese labels instead of raw enum/code text such as `SERVICE`.
3. Unknown fee-type fallback text on this page remains Chinese and does not expose raw technical codes.

## Explicit Non-Closure

This task does not:

- modify backend code, commission API wrappers/types, route params, permissions, response envelopes, or list fetch behavior.
- change commission settlement, commission generation, rule management, stage calculation, filters, query params, pagination, export, or print behavior.
- convert the fee-type field into a selector or introduce a shared display-text registry.
- close display issues outside `CommissionList.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-COMMISSION-SETTLEMENT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-COMMISSION-LIST-TERM-LABELS-01.md`
- `frontend/src/modules/commission/pages/CommissionList.vue`
- `artifacts/AD-FE-COMMISSION-LIST-TERM-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-COMMISSION-LIST-TERM-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/commission/pages/CommissionList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-COMMISSION-LIST-TERM-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-COMMISSION-LIST-TERM-LABELS-01 ux_check /bin/zsh -lc '! rg -n "placeholder=\"案卷号\"|label=\"案卷号\"|\\{\\{ row\\.fee_type|return map\\[type\\] \\|\\| type" frontend/src/modules/commission/pages/CommissionList.vue && rg -n "placeholder=\"案号\"|label=\"案号\"|formatFeeTypeDisplay|未知费用类型|服务费" frontend/src/modules/commission/pages/CommissionList.vue'
./scripts/evidence_run.sh AD-FE-COMMISSION-LIST-TERM-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-COMMISSION-LIST-TERM-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-COMMISSION-LIST-TERM-LABELS-01/results.jsonl`
- `artifacts/AD-FE-COMMISSION-LIST-TERM-LABELS-01/summary.md`
- `artifacts/AD-FE-COMMISSION-LIST-TERM-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-COMMISSION-LIST-TERM-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-COMMISSION-LIST-TERM-LABELS-01/baseline_external_files.txt`
