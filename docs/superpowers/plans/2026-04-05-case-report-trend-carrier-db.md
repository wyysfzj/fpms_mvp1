# CASERPT-TREND-CARRIER-DB-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `backend schema prerequisite only`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Depends On | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `CASERPT-TREND-CARRIER-DB-01` | main thread | `backend/app/modules/cases/models.py`, `backend/alembic/versions/caserpt_trend_carrier_db_01_add_case_terminal_event_dates.py`, `backend/tests/test_case_trend_carrier_schema.py`, `docs/superpowers/specs/2026-04-05-case-report-trend-carrier-db-design.md`, `docs/superpowers/plans/2026-04-05-case-report-trend-carrier-db.md`, `tasks/postenhancement/backend/CASERPT-TREND-CARRIER-DB-01.md` | `CASERPT-TREND-CARRIER-01` | Add persistent case terminal-event date carriers and prove SQLite schema presence | No trend API/UI, no review close update, no other case report residual |
| `CASERPT-QA-TREND-CARRIER-DB-01` | main thread | `tasks/postenhancement/backend/CASERPT-QA-TREND-CARRIER-DB-01.md`, `artifacts/CASERPT-TREND-CARRIER-DB-01/**`, `artifacts/CASERPT-QA-TREND-CARRIER-DB-01/**` | `CASERPT-TREND-CARRIER-DB-01` | Audit evidence, scope, and gates for the DB prerequisite wave | No product-code changes, no trend implementation, no review baseline update |

## Execution Order

1. `CASERPT-TREND-CARRIER-DB-01`
2. `CASERPT-QA-TREND-CARRIER-DB-01`
