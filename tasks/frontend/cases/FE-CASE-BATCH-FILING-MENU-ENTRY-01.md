# FE-CASE-BATCH-FILING-MENU-ENTRY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low

## chosen_runbook

P0-single-lane-story

## Exact Closure Slice

Add one sidebar menu entry under the existing `业务实体` case area so users can open the existing batch filing route `/cases/batch-filing` from the UI.

The menu entry must:

- use Simplified Chinese visible text;
- point to the already existing route `/cases/batch-filing`;
- require case read/write permission consistently with case filing operations;
- appear near `案件管理` so the customer demo can access it as a fixed menu entry.

## Explicit Non-Closure

This task does not:

- change the batch filing page behavior;
- change router definitions;
- change backend APIs or permissions;
- change product data, schema, or migrations;
- modify Skeleton Pack assets;
- fix unrelated UI language or document-gate warnings.

## Allowed Files

- `frontend/src/constants/menu.ts`
- `tasks/frontend/cases/FE-CASE-BATCH-FILING-MENU-ENTRY-01.md`
- `artifacts/FE-CASE-BATCH-FILING-MENU-ENTRY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-CASE-BATCH-FILING-MENU-ENTRY-01 test /bin/zsh -lc 'rg -n "case_batch_filing_menu|案件批量递交|/cases/batch-filing" frontend/src/constants/menu.ts && cd frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-CASE-BATCH-FILING-MENU-ENTRY-01 lint /bin/zsh -lc 'cd frontend && npm run lint -- --fix src/constants/menu.ts && npm run lint -- src/constants/menu.ts'
```

```bash
./scripts/evidence_run.sh FE-CASE-BATCH-FILING-MENU-ENTRY-01 task_gate ./scripts/task_validate.sh FE-CASE-BATCH-FILING-MENU-ENTRY-01
```

## Evidence Path

- `artifacts/FE-CASE-BATCH-FILING-MENU-ENTRY-01/results.jsonl`
- `artifacts/FE-CASE-BATCH-FILING-MENU-ENTRY-01/summary.md`
- `artifacts/FE-CASE-BATCH-FILING-MENU-ENTRY-01/git/diff.patch`
- `artifacts/FE-CASE-BATCH-FILING-MENU-ENTRY-01/screenshots/**`

## Remaining Follow-Up Task IDs

- None.
