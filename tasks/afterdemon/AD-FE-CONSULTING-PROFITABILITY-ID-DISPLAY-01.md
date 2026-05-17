# AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01 - consulting profitability visible ID cleanup

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

Remove visible project ID wording/raw case ID fallback from the consulting profitability page.

This closes only:

1. `ConsultingProfitability.vue` no longer uses visible `项目 ID` copy in the search placeholder, validation message, or summary label.
2. `ConsultingProfitability.vue` no longer directly renders `income.case_id || caseId` in the result summary.
3. UUID-like project identifiers are hidden behind a Chinese business placeholder, while non-UUID user-entered project numbers may still be shown.
4. Unknown expense category/status display on this page uses Chinese placeholders rather than rendering raw technical codes.

## Explicit Non-Closure

This task does not:

- modify backend code, billing/expense API contracts, route query names, permissions, response envelopes, or fetch behavior.
- add project/case lookup APIs or any new readable project name contract.
- change profitability calculations, date filtering, income/expense request parameters, pagination, table structure, or error semantics.
- close consulting case creation, fee draft creation, case form/filter, or other consulting display issues.

## Remaining Follow-Up Task IDs

- `AD-FE-CONSULTING-CASE-CREATE-ID-DISPLAY-01`
- `AD-FE-CASE-FORM-ID-LABELS-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01.md`
- `frontend/src/modules/consulting/pages/ConsultingProfitability.vue`
- `artifacts/AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/consulting/pages/ConsultingProfitability.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "项目 ID|income\\.case_id \\|\\| caseId|return CATEGORY_LABELS\\[key\\] \\|\\| key|\\{\\{ row\\.status \\|\\| .—. \\}\\}|请输入项目 ID" frontend/src/modules/consulting/pages/ConsultingProfitability.vue && rg -n "formatProjectDisplay|isUuidLike|项目编号（必填）|未知支出类别|未知状态" frontend/src/modules/consulting/pages/ConsultingProfitability.vue'
./scripts/evidence_run.sh AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CONSULTING-PROFITABILITY-ID-DISPLAY-01/baseline_external_files.txt`
