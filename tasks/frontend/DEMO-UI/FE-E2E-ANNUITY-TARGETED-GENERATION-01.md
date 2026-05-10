# FE-E2E-ANNUITY-TARGETED-GENERATION-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Make the annuity task page/dialog visibly bind generation to the current case number filter or selected case, then show generated tasks by case number.

## Explicit Non-Closure

- Do not generate annuity tasks without visible UI confirmation.
- Do not change backend annuity generation rules.
- Do not modify grant-fee or case status flows.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `frontend/src/api/annuity.ts`
- `frontend/src/api/annuity.types.ts`
- `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- `frontend/src/modules/annuity/components/AnnuityGenerateDialog.vue`
- `tasks/frontend/DEMO-UI/FE-E2E-ANNUITY-TARGETED-GENERATION-01.md`
- `artifacts/FE-E2E-ANNUITY-TARGETED-GENERATION-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-E2E-ANNUITY-TARGETED-GENERATION-01 test /bin/zsh -lc 'cd frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-E2E-ANNUITY-TARGETED-GENERATION-01 lint /bin/zsh -lc 'cd frontend && npm run lint -- src/api/annuity.ts src/api/annuity.types.ts src/modules/annuity/pages/AnnuityTaskList.vue src/modules/annuity/components/AnnuityGenerateDialog.vue'
```

```bash
./scripts/evidence_run.sh FE-E2E-ANNUITY-TARGETED-GENERATION-01 task_gate ./scripts/task_validate.sh FE-E2E-ANNUITY-TARGETED-GENERATION-01
```

## Evidence Path

- `artifacts/FE-E2E-ANNUITY-TARGETED-GENERATION-01/results.jsonl`
- `artifacts/FE-E2E-ANNUITY-TARGETED-GENERATION-01/summary.md`
- `artifacts/FE-E2E-ANNUITY-TARGETED-GENERATION-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None

