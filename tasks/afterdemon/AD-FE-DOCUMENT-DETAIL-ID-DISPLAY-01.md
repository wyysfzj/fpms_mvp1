# AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01 — document detail visible ID cleanup

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

Remove visible raw document internal ID displays from the document detail page.

This closes only:

1. `DocumentDetail.vue` no longer passes `doc.id` as a relation-chain display fallback.
2. `DocumentDetail.vue` no longer renders `#<doc.id>` in the side information panel.
3. `DocumentDetail.vue` uses document ref number, title, or a Chinese business fallback for visible document identity.

## Explicit Non-Closure

This task does not:

- modify backend code, document API wrappers/types, relation chain component, attachment/log components, router/menu behavior, permissions, or response envelopes.
- change document edit, attachment, reply, template hint, direction, doc type, date, or content behavior.
- close raw-ID display issues in document dispatch/create/edit/wizard/list pages or other modules.

## Remaining Follow-Up Task IDs

- `AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01`
- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01.md`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `artifacts/AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/documents/pages/DocumentDetail.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "#\\{\\{ doc\\.id \\}\\}|refNo: doc\\.ref_no \\|\\| doc\\.id" frontend/src/modules/documents/pages/DocumentDetail.vue && rg -n "formatDocumentDisplay|未命名往来文件" frontend/src/modules/documents/pages/DocumentDetail.vue'
./scripts/evidence_run.sh AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DOCUMENT-DETAIL-ID-DISPLAY-01/baseline_external_files.txt`
