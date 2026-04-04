# CASERPT-AGGREGATE-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `CASERPT-AGG-BE-01` | main thread | `backend/app/modules/cases/api.py`, `backend/app/modules/cases/service.py`, `backend/app/modules/cases/schemas.py`, `backend/tests/test_case_report.py` | First wave; FE depends on the summary contract | Extend `GET /cases` summary with `country_counts` and `agent_counts` only | No grant-rate, no trend, no frontend changes, no schema change |
| `CASERPT-AGG-FE-01` | main thread | `frontend/src/api/cases.ts`, `frontend/src/api/cases.types.ts`, `frontend/src/modules/cases/pages/CaseList.vue` | Serialize after `CASERPT-AGG-BE-01`; preserve existing dirty changes in `cases.ts` / `cases.types.ts` | Render country/agent grouped summary cards on `CaseList.vue` and wire new summary fields through API types | No new page, no chart/export, no backend edits beyond API client/types |
| `CASERPT-AGG-QA-01` | main thread | `artifacts/CASERPT-AGG-BE-01/**`, `artifacts/CASERPT-AGG-FE-01/**`, `artifacts/CASERPT-AGG-QA-01/**` | Final wave after BE and FE pass | Audit evidence, gate pass, and exact close summary for the aggregate slice | No product-code changes |

## Verification

- `python3 -m ruff check backend/app/modules/cases/api.py backend/app/modules/cases/service.py backend/app/modules/cases/schemas.py backend/tests/test_case_report.py`
- `cd backend && pytest -q tests/test_case_report.py`
- `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseList.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh CASERPT-AGG-BE-01`
- `./scripts/task_validate.sh CASERPT-AGG-FE-01`
- `./scripts/task_validate.sh CASERPT-AGG-QA-01`

## Waves

- Wave 1: `CASERPT-AGG-BE-01`
- Wave 2: `CASERPT-AGG-FE-01`
- Wave 3: `CASERPT-AGG-QA-01`
