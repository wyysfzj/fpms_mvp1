# CASERPT-RATE-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `resolved by prior semantics freeze`
- `be_fe_coupling`: `shared summary contract across API client and CaseList page`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `CASERPT-RATE-BE-01` | main thread | `backend/app/modules/cases/service.py`, `backend/app/modules/cases/schemas.py`, `backend/tests/test_case_report.py` | Depends on `CASERPT-RATE-SPEC-01` semantics freeze | Extend `GET /cases` summary with grant-rate-related metrics and tests | No trend reporting, no frontend, no schema changes |
| `CASERPT-RATE-FE-01` | main thread | `frontend/src/api/cases.ts`, `frontend/src/api/cases.types.ts`, `frontend/src/modules/cases/pages/CaseList.vue` | Runs after BE summary contract is stable | Render grant-rate-related metrics on existing case report page | No new page, no chart/export, no trend UI |
| `CASERPT-RATE-QA-01` | main thread | `artifacts/CASERPT-RATE-BE-01/**`, `artifacts/CASERPT-RATE-FE-01/**`, `artifacts/CASERPT-RATE-QA-01/**`, `tasks/postenhancement/backend/CASERPT-RATE-QA-01.md` | Runs after BE/FE completion | Audit evidence, gates, and exact close summary for the grant-rate slice | No product-code changes |

## Serialized Shared-file Decisions

- Backend wave owns:
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/tests/test_case_report.py`
- Frontend wave owns:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseList.vue`

## Verification

- `python3 -m ruff format backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_report.py`
- `python3 -m ruff check backend/app/modules/cases/api.py backend/app/modules/cases/service.py backend/app/modules/cases/schemas.py backend/tests/test_case_report.py`
- `cd backend && pytest -q tests/test_case_report.py`
- `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseList.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh CASERPT-RATE-BE-01`
- `./scripts/task_validate.sh CASERPT-RATE-FE-01`
- `./scripts/task_validate.sh CASERPT-RATE-QA-01`

## Done Definition

- backend summary returns all five grant-rate metrics
- frontend renders the new metrics in Simplified Chinese
- grant rate uses frozen semantics and `null` denominator behavior
- trend reporting remains deferred
- required artifacts exist and all task gates pass
