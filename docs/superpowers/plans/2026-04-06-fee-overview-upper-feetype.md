# Fee Overview Upper Fee-Type Semantics Plan

- date: `2026-04-06`
- target: `SPEC 5.11 upper-pane fee-type residual`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: medium
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-prereq-heavy-story`

## Result Shape

- spec/decomposition freeze only
- no implementation

## Batch Manifest

### `FEOVERVIEW-UPPER-FEETYPE-SPEC-01`

- exact closure slice:
  - freeze the truthful first-round authority for the upper-pane `fee_type` filter semantics
  - reject `FeeItem.fee_type` as a pseudo-equivalent closure
  - define the follow-up implementation graph for backend filter and frontend selector
- explicit non-closure:
  - no product implementation
  - no schema/migration
  - no `5.11` close-decision update
  - no `/fee-overview/gov-payments` modification
  - no frontend page modification
- allowlist:
  - `docs/superpowers/specs/2026-04-06-fee-overview-upper-feetype-design.md`
  - `docs/superpowers/plans/2026-04-06-fee-overview-upper-feetype.md`
  - `tasks/postenhancement/backend/FEOVERVIEW-UPPER-FEETYPE-SPEC-01.md`
  - `tasks/postenhancement/backend/FEOVERVIEW-QA-UPPER-FEETYPE-SPEC-01.md`
- verification:
  - `./scripts/evidence_run.sh FEOVERVIEW-UPPER-FEETYPE-SPEC-01 lint test -f docs/superpowers/specs/2026-04-06-fee-overview-upper-feetype-design.md -a -f docs/superpowers/plans/2026-04-06-fee-overview-upper-feetype.md -a -f tasks/postenhancement/backend/FEOVERVIEW-UPPER-FEETYPE-SPEC-01.md -a -f tasks/postenhancement/backend/FEOVERVIEW-QA-UPPER-FEETYPE-SPEC-01.md`
  - `./scripts/evidence_run.sh FEOVERVIEW-UPPER-FEETYPE-SPEC-01 test /bin/zsh -lc "rg -n 'FeeItem\\.fee_type|FeeDraft\\.draft_type|pseudo-closures|FEOVERVIEW-UPPER-FEETYPE-BE-01|FEOVERVIEW-UPPER-FEETYPE-FE-01' docs/superpowers/specs/2026-04-06-fee-overview-upper-feetype-design.md docs/superpowers/plans/2026-04-06-fee-overview-upper-feetype.md tasks/postenhancement/backend/FEOVERVIEW-UPPER-FEETYPE-SPEC-01.md"`
  - `./scripts/task_validate.sh FEOVERVIEW-UPPER-FEETYPE-SPEC-01`
- evidence path:
  - `artifacts/FEOVERVIEW-UPPER-FEETYPE-SPEC-01/**`
- remaining follow-up task ids:
  - `FEOVERVIEW-UPPER-FEETYPE-BE-01`
  - `FEOVERVIEW-UPPER-FEETYPE-FE-01`
  - `FEOVERVIEW-UPPER-FEETYPE-QA-01`

### `FEOVERVIEW-QA-UPPER-FEETYPE-SPEC-01`

- exact closure slice:
  - audit the upper-pane fee-type semantics wave evidence and confirm no product behavior was absorbed
- explicit non-closure:
  - no product-code changes
  - no close-decision update
- allowlist:
  - `tasks/postenhancement/backend/FEOVERVIEW-QA-UPPER-FEETYPE-SPEC-01.md`
  - `artifacts/FEOVERVIEW-UPPER-FEETYPE-SPEC-01/**`
- verification:
  - `./scripts/evidence_run.sh FEOVERVIEW-QA-UPPER-FEETYPE-SPEC-01 lint test -f tasks/postenhancement/backend/FEOVERVIEW-QA-UPPER-FEETYPE-SPEC-01.md -a -f artifacts/FEOVERVIEW-UPPER-FEETYPE-SPEC-01/summary.md -a -f artifacts/FEOVERVIEW-UPPER-FEETYPE-SPEC-01/results.jsonl`
  - `./scripts/evidence_run.sh FEOVERVIEW-QA-UPPER-FEETYPE-SPEC-01 test /bin/zsh -lc "./scripts/task_validate.sh FEOVERVIEW-UPPER-FEETYPE-SPEC-01 && rg -n 'no product implementation|FeeDraft\\.draft_type|FEOVERVIEW-UPPER-FEETYPE-BE-01' artifacts/FEOVERVIEW-UPPER-FEETYPE-SPEC-01/summary.md"`
  - `./scripts/task_validate.sh FEOVERVIEW-QA-UPPER-FEETYPE-SPEC-01`
- evidence path:
  - `artifacts/FEOVERVIEW-QA-UPPER-FEETYPE-SPEC-01/**`
- remaining follow-up task ids:
  - `None`

## Next Natural Follow-up

- `FEOVERVIEW-UPPER-FEETYPE-BE-01`
- reason:
  - once the category authority is frozen, the backend filter contract can be implemented without stretching `FeeItem.fee_type` into a false closure
