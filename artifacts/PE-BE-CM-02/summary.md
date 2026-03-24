# PE-BE-CM-02

Status: PASS

Scope:
- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/enums.py`
- `backend/tests/test_case_fields.py`

Changes:
- added backend schemas for foreign-agent, bio-deposit, PCT, and invalidation payloads
- enforced foreign-agent, bio-deposit, PCT, and invalidation business validation
- switched case create/read/update responses to round-trip deferred Batch 1 fields
- added 11 deferred Batch 1 backend tests and kept existing case field suite green

Validation:
- `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/app/modules/cases/enums.py backend/tests/test_case_fields.py`
- `cd backend && pytest -q tests/test_case_fields.py`
