# PE-BE-CM-02 — Case API/service completion for foreign agent, PCT, invalidation, and bio deposit.

- Source: `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- Type: `service + api`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: complete deferred Batch 1 backend behavior after schema expansion.
- Covered items:
  - `FR-CM-03`
  - `FR-CM-05`
- Allowlist:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/enums.py`
  - `backend/tests/test_case_fields.py`
- Shared ownership files:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/enums.py`
- Out of scope:
  - Batch 2+ scope
  - document generation
  - original-case downstream linkage in module 2
- Acceptance:
  - foreign agent can be created, updated, read back, and validated
  - bio deposits support `0..n` rows with completeness + uniqueness checks
  - PCT fields validate by case type and round-trip in create/detail/update
  - invalidation fields validate by case type and round-trip in create/detail/update
- Verification:
  - `ruff check --fix backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/app/modules/cases/enums.py backend/tests/test_case_fields.py`
  - `ruff format backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/app/modules/cases/enums.py backend/tests/test_case_fields.py`
  - `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/app/modules/cases/enums.py backend/tests/test_case_fields.py`
  - `pytest -q backend/tests/test_case_fields.py`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing backend tests first
- [ ] Implement minimal backend changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
