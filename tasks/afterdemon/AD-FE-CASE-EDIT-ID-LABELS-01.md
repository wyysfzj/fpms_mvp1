# AD-FE-CASE-EDIT-ID-LABELS-01 - case edit visible ID wording cleanup

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

Normalize visible internal-ID wording in the case edit page.

This closes only:

1. `CaseEdit.vue` no longer shows address/original-case/agent/draftor fields with visible `ID` wording.
2. `CaseEdit.vue` no longer shows English technical code examples in touched country/language/address/original-case/agent placeholders.

## Explicit Non-Closure

This task does not:

- modify backend code, case API wrappers/types, route params, permissions, response envelopes, or save behavior.
- add address/original-case/agent selector APIs or any new readable display contract.
- change validation semantics, payload fields, field names, quick client creation, document behavior, or agent split editor behavior.
- change `CaseCreate.vue`, `CaseList.vue`, `CaseBatchFiling.vue`, report pages, or shared components.

## Remaining Follow-Up Task IDs

- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-REPORT-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CASE-EDIT-ID-LABELS-01.md`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `artifacts/AD-FE-CASE-EDIT-ID-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CASE-EDIT-ID-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/cases/pages/CaseEdit.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CASE-EDIT-ID-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CASE-EDIT-ID-LABELS-01 ux_check /bin/zsh -lc '! rg -n "公文地址 ID|账单地址 ID|客户地址主数据 ID|原案 ID|Case ID|代理人 ID|撰写人 ID|例如 CN|例如 US|例如 EN" frontend/src/modules/cases/pages/CaseEdit.vue && rg -n "公文地址|账单地址|请输入客户地址主数据|请输入被攻击原案|请输入代理人|请输入撰写人|国际公开语言代码" frontend/src/modules/cases/pages/CaseEdit.vue'
./scripts/evidence_run.sh AD-FE-CASE-EDIT-ID-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-CASE-EDIT-ID-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-CASE-EDIT-ID-LABELS-01/results.jsonl`
- `artifacts/AD-FE-CASE-EDIT-ID-LABELS-01/summary.md`
- `artifacts/AD-FE-CASE-EDIT-ID-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-CASE-EDIT-ID-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CASE-EDIT-ID-LABELS-01/baseline_external_files.txt`
