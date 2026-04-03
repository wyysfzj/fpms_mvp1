# DOCWIZ-CLOSE-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only close audit after residual program freeze`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-CLOSE-01` | main thread | `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`, `docs/priority-ranked-mitigation-ledger.md`, `docs/superpowers/specs/2026-04-03-docwiz-close-audit-design.md`, `docs/superpowers/plans/2026-04-03-docwiz-close-audit.md` | Depends on Step1/2 representative slices and Step3/4/5 residual contract waves all being PASS | Refresh-close `#8` in review baseline and mitigation ledger | No re-review of `#13/#15/#19`, no new stories, no product-code change |
| `DOCWIZ-QA-CLOSE-01` | monitor / main thread | `artifacts/DOCWIZ-CLOSE-01/**`, `artifacts/DOCWIZ-QA-CLOSE-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-CLOSE-01.md` | Runs after close-audit refresh is complete | Audit evidence and close summary for the `#8` baseline refresh | No product-code changes |

## Verification

- `./scripts/task_validate.sh DOCWIZ-CLOSE-01`
- `./scripts/task_validate.sh DOCWIZ-QA-CLOSE-01`

## Done Definition

- `#8` is updated from `Partially Closed` to `Closed`
- Top-level counts and mitigation ledger are consistent with that decision
- Required artifacts exist and both task gates pass
