# COMMSPLIT-CLOSE-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only audit on top of frozen and implemented backend/frontend slices`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `COMMSPLIT-CLOSE-01` | main thread | `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`, `docs/priority-ranked-mitigation-ledger.md` | Depends on committed COMMSPLIT BE/FE evidence chain through `675c0e1` | Reclassify `P1 #5` from `Still Missing` to current truthful status and update global counts/queue accordingly | No product-code changes; no re-audit of unrelated items |
| `COMMSPLIT-QA-10` | monitor / main thread | `artifacts/COMMSPLIT-CLOSE-01/**`, `artifacts/COMMSPLIT-QA-10/**`, `tasks/postenhancement/backend/COMMSPLIT-QA-10.md` | Runs after doc updates and diff capture | Audit close-refresh evidence and validate task gates | No product-code changes outside audit evidence |

## Verification

- `./scripts/task_validate.sh COMMSPLIT-CLOSE-01`
- `./scripts/task_validate.sh COMMSPLIT-QA-10`

## Done Definition

- `docs/FPMS_SPEC2_2nd_Review_REFRESH.md` no longer says `#5` is `Still Missing`
- `docs/priority-ranked-mitigation-ledger.md` no longer lists `#5` as non-closed
- Summary counts and priority queue are internally consistent
- Required artifacts exist and both task gates pass
