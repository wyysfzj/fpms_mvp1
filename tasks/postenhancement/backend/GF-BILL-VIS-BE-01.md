# GF-BILL-VIS-BE-01

- chosen_runbook: `P0-frontend-heavy-story`
- exact closure slice: extend grant-fee worklist payload with bill visibility fields derived from existing draft-to-bill lineage
- explicit non-closure: no billing write path, no new state, no receipt/payment semantics
- allowlist:
  - `backend/app/modules/grant_fees/service.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/tests/test_grant_fee_worklist_api.py`
- verification:
  - `python3 -m ruff format backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_worklist_api.py`
  - `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_worklist_api.py`
  - `cd backend && pytest -q tests/test_grant_fee_worklist_api.py`
- evidence path: `artifacts/GF-BILL-VIS-BE-01`
- remaining follow-up task ids:
  - `GF-BILL-VIS-FE-01`
  - `GF-BILL-VIS-QA-01`

