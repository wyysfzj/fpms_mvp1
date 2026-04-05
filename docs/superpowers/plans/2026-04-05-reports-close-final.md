# REPORTS-CLOSE-03 Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `doc-only close audit after product evidence`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Depends On | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `REPORTS-CLOSE-03` | main thread | `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`, `docs/priority-ranked-mitigation-ledger.md`, `docs/superpowers/specs/2026-04-05-reports-close-final-design.md`, `docs/superpowers/plans/2026-04-05-reports-close-final.md`, `tasks/postenhancement/backend/REPORTS-CLOSE-03.md` | `CASERPT-TREND-MIG-MERGE-01`, `CASERPT-TREND-BE-01`, `CASERPT-TREND-FE-01`, `CASERPT-TREND-QA-01` | Refresh `#13` from `Partially Closed` to `Closed` based on current product evidence | No product-code changes, no re-review of `#15/#19`, no new residual stories |
| `REPORTS-QA-CLOSE-03` | main thread | `tasks/postenhancement/backend/REPORTS-QA-CLOSE-03.md`, `artifacts/REPORTS-CLOSE-03/**`, `artifacts/REPORTS-QA-CLOSE-03/**` | `REPORTS-CLOSE-03` | Audit evidence and close summary for the final reports close refresh | No product-code changes |
