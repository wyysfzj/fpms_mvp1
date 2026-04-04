# REPORTS-CLOSE-02 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only close audit after residual implementation waves`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `REPORTS-CLOSE-02` | main thread | `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`, `docs/priority-ranked-mitigation-ledger.md`, `docs/superpowers/specs/2026-04-05-reports-product-close-audit-design.md`, `docs/superpowers/plans/2026-04-05-reports-product-close-audit.md`, `tasks/postenhancement/backend/REPORTS-CLOSE-02.md` | Depends on `REPORTS-LEDGER-01`, `CASERPT-*`, `FEERPT-*`, and `ANNRPT-*` residual waves being PASS | Refresh `#13` from `Needs Reclassification` to `Partially Closed` in review baseline and mitigation ledger | No product-code change, no re-review of `#15/#19`, no new residual stories |
| `REPORTS-QA-CLOSE-02` | monitor / main thread | `artifacts/REPORTS-CLOSE-02/**`, `artifacts/REPORTS-QA-CLOSE-02/**`, `tasks/postenhancement/backend/REPORTS-QA-CLOSE-02.md` | Runs after close-audit refresh is complete | Audit evidence and close summary for the `#13` product close refresh | No product-code changes |

## Verification

- `./scripts/task_validate.sh REPORTS-CLOSE-02`
- `./scripts/task_validate.sh REPORTS-QA-CLOSE-02`

## Done Definition

- `#13` is updated from `Needs Reclassification` to `Partially Closed`
- top-level counts and mitigation ledger are consistent with that decision
- `#13` remains in the mitigation ledger with narrowed family-residual wording
- required artifacts exist and both task gates pass
