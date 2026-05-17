# AD-FE-FEE-RATES-ID-LABELS-01 - fee rates visible ID and raw code cleanup

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

Remove visible internal fee-rate ID and raw enum fallbacks from the fee rates page.

This closes only:

1. `FeeRates.vue` no longer renders the internal `id` column as a visible number.
2. Unknown fee type/rate group/calculation mode/case type/patent category display on this page uses Chinese placeholders rather than raw technical codes.

## Explicit Non-Closure

This task does not:

- modify backend code, fee API wrappers/types, route params, permissions, response envelopes, or list fetch behavior.
- change fee rate create/edit dialog behavior, payloads, validation, pagination, or table actions.
- change shared display constants or close fee display issues outside `FeeRates.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-COMMISSION-RULE-LIST-ID-LABELS-01`
- `AD-FE-CASE-FORM-ID-LABELS-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-FEE-RATES-ID-LABELS-01.md`
- `frontend/src/modules/fees/pages/FeeRates.vue`
- `artifacts/AD-FE-FEE-RATES-ID-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-FEE-RATES-ID-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/fees/pages/FeeRates.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-FEE-RATES-ID-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-FEE-RATES-ID-LABELS-01 ux_check /bin/zsh -lc '! rg -n "prop=\"id\" label=\"编号\"|\\?\\? v|\\?\\? v\\)|\\|\\| v" frontend/src/modules/fees/pages/FeeRates.vue && rg -n "unknownLabel|未知费用类型|未知费率组|未知计算模式|未知案件类型|未知专利类别" frontend/src/modules/fees/pages/FeeRates.vue'
./scripts/evidence_run.sh AD-FE-FEE-RATES-ID-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-FEE-RATES-ID-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-FEE-RATES-ID-LABELS-01/results.jsonl`
- `artifacts/AD-FE-FEE-RATES-ID-LABELS-01/summary.md`
- `artifacts/AD-FE-FEE-RATES-ID-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-FEE-RATES-ID-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-FEE-RATES-ID-LABELS-01/baseline_external_files.txt`
