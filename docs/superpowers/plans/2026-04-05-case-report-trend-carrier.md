# CASERPT-TREND-CARRIER-01 Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `prerequisite freeze before implementation`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `CASERPT-TREND-CARRIER-01` | main thread | `docs/superpowers/specs/2026-04-05-case-report-trend-carrier-design.md`, `docs/superpowers/plans/2026-04-05-case-report-trend-carrier.md`, `tasks/postenhancement/backend/CASERPT-TREND-CARRIER-01.md`, `tasks/postenhancement/backend/CASERPT-QA-TREND-CARRIER-01.md` | Depends on current `RPT-CASE` product evidence and `CASERPT-TREND-PREREQ-01` | Freeze the remaining carrier blocker for case trend reporting and keep `CASERPT-TREND-01` blocked | No schema/migration change, no BE/FE trend implementation, no `#13` close update |
| `CASERPT-QA-TREND-CARRIER-01` | main thread | `artifacts/CASERPT-TREND-CARRIER-01/**`, `artifacts/CASERPT-QA-TREND-CARRIER-01/**`, `tasks/postenhancement/backend/CASERPT-QA-TREND-CARRIER-01.md` | Runs after the carrier freeze | Audit evidence and close summary for the carrier-blocker wave | No product-code changes |

## Verification

- `./scripts/task_validate.sh CASERPT-TREND-CARRIER-01`
- `./scripts/task_validate.sh CASERPT-QA-TREND-CARRIER-01`
