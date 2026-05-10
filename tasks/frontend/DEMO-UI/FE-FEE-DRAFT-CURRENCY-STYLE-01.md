# FE-FEE-DRAFT-CURRENCY-STYLE-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Fee draft detail and list money rendering must tolerate blank, whitespace, or invalid currency values by falling back to `CNY`, so visible UI navigation no longer throws `Currency code is required with currency style`.

## Explicit Non-Closure

- Do not change backend fee draft currency persistence.
- Do not change fee draft creation, locking, billing, or pay-list generation semantics.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `frontend/src/utils/money.ts`
- `frontend/tests/money-format.mjs`
- `frontend/src/modules/fees/pages/FeeDraftDetail.vue`
- `frontend/src/modules/fees/pages/FeeDraftList.vue`
- `tasks/frontend/DEMO-UI/FE-FEE-DRAFT-CURRENCY-STYLE-01.md`
- `artifacts/FE-FEE-DRAFT-CURRENCY-STYLE-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-FEE-DRAFT-CURRENCY-STYLE-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && rm -rf .tmp-money-test && npx tsc src/utils/money.ts --target ES2020 --module ES2020 --moduleResolution node --outDir .tmp-money-test --skipLibCheck && node tests/money-format.mjs'
```

```bash
./scripts/evidence_run.sh FE-FEE-DRAFT-CURRENCY-STYLE-01 lint /bin/zsh -lc 'cd frontend && npm run lint'
```

```bash
./scripts/evidence_run.sh FE-FEE-DRAFT-CURRENCY-STYLE-01 task_gate ./scripts/task_validate.sh FE-FEE-DRAFT-CURRENCY-STYLE-01
```

## Evidence Path

- `artifacts/FE-FEE-DRAFT-CURRENCY-STYLE-01/results.jsonl`
- `artifacts/FE-FEE-DRAFT-CURRENCY-STYLE-01/summary.md`
- `artifacts/FE-FEE-DRAFT-CURRENCY-STYLE-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None
