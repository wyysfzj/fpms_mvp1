# Fee Overview Plan

- date: `2026-04-06`
- target: `SPEC 5.11 prerequisite authority`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-prereq-heavy-story`

## Result Shape

- prerequisite/spec freeze only
- no implementation

## Batch Manifest

### `FEOVERVIEW-SPEC-01`

- exact closure slice:
  - freeze `SPEC 5.11` pane authority and reject reinterpretation of the current unified query as a near-equivalent implementation
  - define follow-up implementation graph for upper/lower pane and shared frontend page
- explicit non-closure:
  - no product implementation
  - no schema/migration
  - no final-audit update
  - no `/fee-unified-query` modifications
- allowlist:
  - `docs/superpowers/specs/2026-04-06-fee-overview-design.md`
  - `docs/superpowers/plans/2026-04-06-fee-overview.md`
  - `tasks/postenhancement/backend/FEOVERVIEW-SPEC-01.md`
  - `tasks/postenhancement/backend/FEOVERVIEW-QA-PLAN-01.md`
- verification:
  - `./scripts/evidence_run.sh FEOVERVIEW-SPEC-01 lint test -f docs/superpowers/specs/2026-04-06-fee-overview-design.md -a -f docs/superpowers/plans/2026-04-06-fee-overview.md -a -f tasks/postenhancement/backend/FEOVERVIEW-SPEC-01.md -a -f tasks/postenhancement/backend/FEOVERVIEW-QA-PLAN-01.md`
  - `./scripts/evidence_run.sh FEOVERVIEW-SPEC-01 test /bin/zsh -lc "rg -n 'P0-prereq-heavy-story|upper pane|lower pane|current unified query|FEOVERVIEW-UPPER-BE-01|FEOVERVIEW-FE-01' docs/superpowers/specs/2026-04-06-fee-overview-design.md docs/superpowers/plans/2026-04-06-fee-overview.md tasks/postenhancement/backend/FEOVERVIEW-SPEC-01.md"`
  - `./scripts/task_validate.sh FEOVERVIEW-SPEC-01`
- evidence path:
  - `artifacts/FEOVERVIEW-SPEC-01/**`
- remaining follow-up task ids:
  - `FEOVERVIEW-UPPER-BE-01`
  - `FEOVERVIEW-LOWER-BE-01`
  - `FEOVERVIEW-FE-01`
  - `FEOVERVIEW-QA-01`

### `FEOVERVIEW-QA-PLAN-01`

- exact closure slice:
  - audit the fee-overview prerequisite-wave evidence and confirm no product behavior was absorbed
- explicit non-closure:
  - no product-code changes
  - no close-decision update
- allowlist:
  - `tasks/postenhancement/backend/FEOVERVIEW-QA-PLAN-01.md`
  - `artifacts/FEOVERVIEW-SPEC-01/**`
- verification:
  - `./scripts/evidence_run.sh FEOVERVIEW-QA-PLAN-01 lint test -f tasks/postenhancement/backend/FEOVERVIEW-QA-PLAN-01.md -a -f artifacts/FEOVERVIEW-SPEC-01/summary.md -a -f artifacts/FEOVERVIEW-SPEC-01/results.jsonl`
  - `./scripts/evidence_run.sh FEOVERVIEW-QA-PLAN-01 test /bin/zsh -lc "./scripts/task_validate.sh FEOVERVIEW-SPEC-01 && rg -n 'no product implementation|FEOVERVIEW-UPPER-BE-01|FEOVERVIEW-LOWER-BE-01|FEOVERVIEW-FE-01' artifacts/FEOVERVIEW-SPEC-01/summary.md"`
  - `./scripts/task_validate.sh FEOVERVIEW-QA-PLAN-01`
- evidence path:
  - `artifacts/FEOVERVIEW-QA-PLAN-01/**`
- remaining follow-up task ids:
  - `None`

## Next Natural Follow-up

- `FEOVERVIEW-UPPER-BE-01`
- reason:
  - the upper `GovPayment` pane is the clearest first implementation slice once pane authority is frozen
