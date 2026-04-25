# FE-DOCUMENT-CASE-SELECTORS-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Replace document create/edit raw case-id entry with an existing-backend case selector so users can choose a case by business-facing case number/title/client.

This task closes only:

1. `DocumentCreate.vue` non-locked case context uses an `el-select` populated by existing `getCases()`.
2. `DocumentEdit.vue` uses an `el-select` populated by existing `getCases()`.
3. Selected values remain backend `case_id` values in existing create/update payloads.
4. Existing locked case context behavior in `DocumentCreate.vue` remains unchanged.
5. Reply-source document loading continues to use the selected `case_id`.

## Explicit Non-Closure

Do not:

- modify backend code.
- modify document API wrappers or types.
- modify document wizard batch parsing or submission.
- modify document dispatch/envelope flows.
- add agent/user selectors.
- change document permission behavior.
- change route/menu wiring.
- change skeleton data or automation handlers.

## Remaining Follow-Up Task IDs

- `FE-PAYLIST-CLIENT-CASE-SELECTORS-01`
- `PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01`
- `PRODUCT-FE-PAYLIST-MANUAL-FEE-ITEM-SELECTOR-CONTRACT-01`
- `PRODUCT-COMMISSION-BILL-NO-QUERY-CONTRACT-01`

## Allowed Files

- `tasks/frontend/FE-DOCUMENT-CASE-SELECTORS-01.md`
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `frontend/src/modules/documents/pages/DocumentEdit.vue`
- `artifacts/FE-DOCUMENT-CASE-SELECTORS-01/**`

## Verification Commands

Run from repo root unless noted:

```bash
./scripts/evidence_run.sh FE-DOCUMENT-CASE-SELECTORS-01 red /bin/zsh -lc 'rg -n "请选择案件|caseOptions|formatCaseOption|fetchCaseOptions" frontend/src/modules/documents/pages/DocumentCreate.vue frontend/src/modules/documents/pages/DocumentEdit.vue'
./scripts/evidence_run.sh FE-DOCUMENT-CASE-SELECTORS-01 lint /bin/zsh -lc 'cd frontend && npm run typecheck'
./scripts/evidence_run.sh FE-DOCUMENT-CASE-SELECTORS-01 test /bin/zsh -lc 'cd frontend && npm run build'
./scripts/evidence_run.sh FE-DOCUMENT-CASE-SELECTORS-01 ux_check /bin/zsh -lc 'rg -n "请选择案件|caseOptions|formatCaseOption|fetchCaseOptions|查看案件列表" frontend/src/modules/documents/pages/DocumentCreate.vue frontend/src/modules/documents/pages/DocumentEdit.vue'
./scripts/evidence_run.sh FE-DOCUMENT-CASE-SELECTORS-01 task_gate ./scripts/task_validate.sh FE-DOCUMENT-CASE-SELECTORS-01
```

## Evidence Path

- `artifacts/FE-DOCUMENT-CASE-SELECTORS-01/results.jsonl`
- `artifacts/FE-DOCUMENT-CASE-SELECTORS-01/summary.md`
- `artifacts/FE-DOCUMENT-CASE-SELECTORS-01/git/diff.patch`
- `artifacts/FE-DOCUMENT-CASE-SELECTORS-01/baseline_allowlist.diff`
- `artifacts/FE-DOCUMENT-CASE-SELECTORS-01/baseline_external_files.txt`
