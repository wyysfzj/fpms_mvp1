# AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01 - fee draft list ID column label cleanup

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

Remove internal-ID column semantics from the fee draft list display column.

This closes only:

1. `FeeDraftList.vue` no longer binds the visible draft display column to `prop="id"`.
2. `FeeDraftList.vue` no longer labels the visible draft display column as `草稿编号`.
3. Internal draft IDs remain route/navigation values only.

## Explicit Non-Closure

This task does not:

- modify backend code, fee API wrappers/types, route params, permissions, response envelopes, or list fetch behavior.
- change draft display text, row click/detail navigation, filters, pagination, status/type mapping, amount formatting, or fee draft detail pages.
- change shared label constants.

## Remaining Follow-Up Task IDs

- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01.md`
- `frontend/src/modules/fees/pages/FeeDraftList.vue`
- `artifacts/AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/fees/pages/FeeDraftList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01 ux_check /bin/zsh -lc '! rg -n "prop=\"id\" :label=\"ZH\\.feeList\\.draftId\"|草稿编号" frontend/src/modules/fees/pages/FeeDraftList.vue && rg -n "label=\"费用草稿\"|getDraftDisplay" frontend/src/modules/fees/pages/FeeDraftList.vue'
./scripts/evidence_run.sh AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01 task_gate ./scripts/task_validate.sh AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01
```

## Evidence Path

- `artifacts/AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01/results.jsonl`
- `artifacts/AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01/summary.md`
- `artifacts/AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01/git/diff.patch`
- `artifacts/AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01/baseline_allowlist.diff`
- `artifacts/AD-FE-FEE-DRAFT-LIST-ID-COLUMN-LABEL-01/baseline_external_files.txt`
