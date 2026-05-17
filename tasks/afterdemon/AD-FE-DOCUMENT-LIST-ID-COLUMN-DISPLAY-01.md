# AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01 - document list visible ID column cleanup

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

Remove the visible internal document ID column from the document list page.

This closes only:

1. `DocumentList.vue` no longer renders `prop="id"` as a visible list column.
2. Document navigation continues to use internal IDs only in route values and API calls.

## Explicit Non-Closure

This task does not:

- modify backend code, document API wrappers/types, route params, permissions, response envelopes, or list fetch behavior.
- change document filters, pagination, sorting, navigation, direction/type mapping, template display, or document detail/create/edit pages.
- change shared label constants or close raw-ID display issues outside `DocumentList.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-DOCUMENT-ENVELOPE-ID-DISPLAY-01`
- `AD-FE-CASE-FORM-ID-LABELS-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01.md`
- `frontend/src/modules/documents/pages/DocumentList.vue`
- `artifacts/AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/documents/pages/DocumentList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "prop=\"id\" :label=\"ZH\\.docList\\.id\"|prop=\"id\" label=\"编号\"|\\{\\{ row\\.id \\}\\}" frontend/src/modules/documents/pages/DocumentList.vue && rg -n "ZH\\.docList\\.direction|formatCaseDisplay" frontend/src/modules/documents/pages/DocumentList.vue'
./scripts/evidence_run.sh AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01/summary.md`
- `artifacts/AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DOCUMENT-LIST-ID-COLUMN-DISPLAY-01/baseline_external_files.txt`
