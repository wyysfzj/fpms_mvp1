# MDPRE-BE-01

## Summary

- Added list-only backend skeleton endpoints for `/api/v1/applicants` and `/api/v1/countries`.
- Added matching schemas and services so Applicant/Country now share a stable prerequisite list contract shape.
- Wired the new routers into the module-level API router.
- Froze permission namespaces to `Applicant.Read` / `Applicant.Write` and `Country.Read` / `Country.Write`, without introducing object-level CRUD permission semantics.
- Kept scope intentionally thin: no create/update behavior, no selector/case linkage, no frontend work.

## Verification

- `python3 -m ruff check backend/app/modules/masterdata/applicants/api.py backend/app/modules/masterdata/applicants/schemas.py backend/app/modules/masterdata/applicants/service.py backend/app/modules/masterdata/countries/api.py backend/app/modules/masterdata/countries/schemas.py backend/app/modules/masterdata/countries/service.py backend/app/api/router.py backend/tests/test_masterdata_prereq_contract.py backend/app/modules/rbac/service.py` -> pass
- `cd backend && PYTHONPATH=. pytest -q tests/test_masterdata_prereq_contract.py` -> pass
- `./scripts/task_validate.sh MDPRE-BE-01` -> pass

## Evidence

- `artifacts/MDPRE-BE-01/results.jsonl`
- `artifacts/MDPRE-BE-01/git/diff.patch`
- `artifacts/MDPRE-BE-01/baseline_external_files.txt`
