# PD-P1-BE-FILING-PACKAGE-API-01 — Filing preparation package API

## Exact Closure Slice

Add the backend API resource for new-application filing preparation: read package, refresh checklist/manifest from case/documents/fees, update checklist review state, and record external-operation timestamps needed by P1.

## Explicit Non-Closure

No direct CPC/official submission. No XML generation. No official-site login/signature/submit. No frontend implementation.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-FILING-PREP-01`
- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `backend/app/api/router.py`
- `backend/app/modules/official_workflows/api.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_pd_p1_filing_package_api.py`
- `tasks/postdemo/PD-P1-BE-FILING-PACKAGE-API-01.md`
- `artifacts/PD-P1-BE-FILING-PACKAGE-API-01/**`

## Verification Commands

- `ruff check --fix backend/app/api/router.py backend/app/modules/official_workflows backend/tests/test_pd_p1_filing_package_api.py`
- `ruff format backend/app/api/router.py backend/app/modules/official_workflows backend/tests/test_pd_p1_filing_package_api.py`
- `ruff check backend/app/api/router.py backend/app/modules/official_workflows backend/tests/test_pd_p1_filing_package_api.py`
- `cd backend && pytest -q tests/test_pd_p1_filing_package_api.py`
- `./scripts/task_validate.sh PD-P1-BE-FILING-PACKAGE-API-01`

## Evidence Path

- `artifacts/PD-P1-BE-FILING-PACKAGE-API-01/`

## Acceptance

- Permission is injected as `_perm: None = Depends(require_perm("OfficialWorkflow.Read"|"OfficialWorkflow.Update"))`.
- Response includes official field completeness, technical disclosure gate, commission instruction conditional gate, filing file roles, official-page checklist, XML zip placeholder/reference, merged PDF/archive status, and fee summary.
