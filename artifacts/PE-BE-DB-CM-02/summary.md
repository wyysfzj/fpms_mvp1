# PE-BE-DB-CM-02

Status: PASS

Scope:
- `backend/app/modules/cases/models.py`
- `backend/alembic/versions/pe_be_db_cm_02_case_ext_fields.py`

Changes:
- added Case persistence for `foreign_agent_id`, `foreign_ref`, PCT fields, invalidation fields
- added `T_BioDeposit` ORM model
- added SQLite-safe migration for deferred Batch 1 case fields and `t_bio_deposit`

Validation:
- `ruff check backend/app/modules/cases/models.py backend/alembic/versions/pe_be_db_cm_02_case_ext_fields.py`
- `cd backend && pytest -q tests/test_case_fields.py -k "DeferredBatch1Fields or foreign_agent or pct or invalidation or bio_deposit"`
