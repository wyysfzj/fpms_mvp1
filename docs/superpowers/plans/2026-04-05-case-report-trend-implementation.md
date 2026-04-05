# CASERPT-TREND-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared summary contract on existing page`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Depends On | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `CASERPT-TREND-BE-01` | main thread | `backend/app/modules/cases/service.py`, `backend/app/modules/cases/schemas.py`, `backend/tests/test_case_report.py`, `docs/superpowers/specs/2026-04-05-case-report-trend-implementation-design.md`, `docs/superpowers/plans/2026-04-05-case-report-trend-implementation.md`, `tasks/postenhancement/backend/CASERPT-TREND-BE-01.md` | `CASERPT-TREND-CARRIER-DB-01` | Add year/month case trend summary rows to `GET /cases` | No frontend visibility, no charts/export, no close update |
| `CASERPT-TREND-FE-01` | main thread | `frontend/src/api/cases.ts`, `frontend/src/api/cases.types.ts`, `frontend/src/modules/cases/pages/CaseList.vue`, `tasks/postenhancement/frontend/CASERPT-TREND-FE-01.md` | `CASERPT-TREND-BE-01` | Render year/month case trend summaries on existing case list page | No new page, no charts/export, no close update |
| `CASERPT-TREND-QA-01` | main thread | `tasks/postenhancement/backend/CASERPT-TREND-QA-01.md`, `artifacts/CASERPT-TREND-BE-01/**`, `artifacts/CASERPT-TREND-FE-01/**`, `artifacts/CASERPT-TREND-QA-01/**` | `CASERPT-TREND-BE-01`, `CASERPT-TREND-FE-01` | Audit evidence, gates, and exact closure for trend implementation wave | No product-code changes, no review baseline update |

## Execution Order

1. `CASERPT-TREND-BE-01`
2. `CASERPT-TREND-FE-01`
3. `CASERPT-TREND-QA-01`
