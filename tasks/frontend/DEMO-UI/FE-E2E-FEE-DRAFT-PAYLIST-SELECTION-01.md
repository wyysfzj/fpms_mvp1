# FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

On a locked fee draft detail page, official fee rows remain selectable through visible UI controls and selecting at least one GOV row enables `生成官费清单`.

## Explicit Non-Closure

- Do not change fee draft lock/unlock semantics.
- Do not change pay-list backend creation semantics.
- Do not auto-create pay lists without visible UI row selection.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `frontend/src/modules/fees/components/FeeDraftItemsTable.vue`
- `tasks/frontend/DEMO-UI/FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01.md`
- `artifacts/FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01 test /bin/zsh -lc 'cd frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01 lint /bin/zsh -lc 'cd frontend && npm run lint -- src/modules/fees/components/FeeDraftItemsTable.vue'
```

```bash
./scripts/evidence_run.sh FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01 task_gate ./scripts/task_validate.sh FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01
```

## Evidence Path

- `artifacts/FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01/results.jsonl`
- `artifacts/FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01/summary.md`
- `artifacts/FE-E2E-FEE-DRAFT-PAYLIST-SELECTION-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None

