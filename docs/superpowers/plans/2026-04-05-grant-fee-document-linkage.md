# GF-DOC-SPEC-01 Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `semantics freeze before linkage implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

1. `GF-DOC-SPEC-01`
   - closure: freeze grant-fee document/reminder linkage semantics and identify the first minimal follow-up slice
   - non-closure: no product-code changes
2. `GF-QA-DOC-SPEC-01`
   - closure: validate evidence, scope, and readiness of the semantics freeze
   - non-closure: no product-code changes

## Verification

- `./scripts/evidence_run.sh GF-DOC-SPEC-01 lint test -f docs/superpowers/specs/2026-04-05-grant-fee-document-linkage-design.md`
- `./scripts/evidence_run.sh GF-DOC-SPEC-01 test /bin/zsh -lc "test -f docs/superpowers/specs/2026-04-05-grant-fee-document-linkage-design.md && rg -n 'notice_sent|notify_count|GF-NOTICE-VIS-01|Document|Task' docs/superpowers/specs/2026-04-05-grant-fee-document-linkage-design.md"`
- `./scripts/evidence_run.sh GF-QA-DOC-SPEC-01 lint test -f tasks/postenhancement/backend/GF-QA-DOC-SPEC-01.md`
- `./scripts/evidence_run.sh GF-QA-DOC-SPEC-01 test /bin/zsh -lc "test -f artifacts/GF-DOC-SPEC-01/summary.md && rg -n 'GF-NOTICE-VIS-01|no product implementation|document/reminder linkage' tasks/postenhancement/backend/GF-QA-DOC-SPEC-01.md artifacts/GF-DOC-SPEC-01/summary.md"`
- `./scripts/task_validate.sh GF-DOC-SPEC-01`
- `./scripts/task_validate.sh GF-QA-DOC-SPEC-01`

