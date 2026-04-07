# Module 6 FR-COM-07 提成结算报表导出 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `medium`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

| Wave | Task ID | Owner | Allowlist | Verification |
|---|---|---|---|---|
| 1 | `COMMRPT-EXPORT-BE-01` | main thread | `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, `backend/app/modules/commission/export_excel.py`, `backend/tests/test_commission_report.py` | `python3 -m ruff check backend/app/modules/commission/api.py backend/app/modules/commission/service.py backend/app/modules/commission/export_excel.py backend/tests/test_commission_report.py`, `cd backend && pytest -q tests/test_commission_report.py`, `./scripts/task_validate.sh COMMRPT-EXPORT-BE-01` |
| 2 | `COMMRPT-EXPORT-FE-01` | main thread | `frontend/src/api/commission.ts`, `frontend/src/api/commission.types.ts`, `frontend/src/modules/commission/pages/CommissionSettlement.vue` | `cd frontend && npm run lint -- src/api/commission.ts src/api/commission.types.ts src/modules/commission/pages/CommissionSettlement.vue`, `cd frontend && npm run typecheck`, `./scripts/task_validate.sh COMMRPT-EXPORT-FE-01` |
| 3 | `COMMRPT-EXPORT-QA-01` | main thread | `artifacts/COMMRPT-EXPORT-BE-01/**`, `artifacts/COMMRPT-EXPORT-FE-01/**`, `artifacts/COMMRPT-EXPORT-QA-01/**`, `tasks/postenhancement/backend/COMMRPT-EXPORT-QA-01.md` | `./scripts/task_validate.sh COMMRPT-EXPORT-QA-01` |
| 4 | `COMMRPT-CLOSE-01` | main thread | `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`, `docs/superpowers/specs/2026-04-06-commission-report-export-design.md`, `docs/superpowers/plans/2026-04-06-commission-report-export.md`, `tasks/postenhancement/backend/COMMRPT-CLOSE-01.md`, `tasks/postenhancement/backend/COMMRPT-QA-CLOSE-01.md` | `./scripts/task_validate.sh COMMRPT-CLOSE-01` |
| 5 | `COMMRPT-QA-CLOSE-01` | main thread | `artifacts/COMMRPT-CLOSE-01/**`, `artifacts/COMMRPT-QA-CLOSE-01/**`, `tasks/postenhancement/backend/COMMRPT-QA-CLOSE-01.md` | `./scripts/task_validate.sh COMMRPT-QA-CLOSE-01` |

## Exact Closure Slice

- `COMMRPT-EXPORT-BE-01`
  - add truthful settlement-report export endpoint using existing report filters
- `COMMRPT-EXPORT-FE-01`
  - add report export button and download path on the existing settlement report page
- `COMMRPT-EXPORT-QA-01`
  - audit implementation evidence only
- `COMMRPT-CLOSE-01`
  - refresh final-audit Module 6 residual if committed evidence closes `FR-COM-07`

## Explicit Non-closure

- no print
- no settlement CRUD changes
- no new aggregation semantics
- no refactor of unrelated commission code
