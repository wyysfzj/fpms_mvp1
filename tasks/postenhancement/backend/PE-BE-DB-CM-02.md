# PE-BE-DB-CM-02 — Case schema expansion for foreign agent, PCT, invalidation, and bio deposit.

- Source: `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- Source: `docs/FPMS_Batch1_Scope_Adjustment_20260315.md`
- Type: `migration + model`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: add the minimum persistence needed to close deferred `FR-CM-03` and `FR-CM-05`.
- Covered items:
  - `FR-CM-03`
  - `FR-CM-05`
- Allowlist:
  - `backend/alembic/versions/*.py`
  - `backend/app/modules/cases/models.py`
- Shared ownership files:
  - `backend/app/modules/cases/models.py`
- Out of scope:
  - any Batch 2+ feature
  - document generation
  - unrelated masterdata redesign
  - introduction of `T_BioDepositUnit`
- Acceptance:
  - `t_case` persists foreign-agent, PCT, and invalidation fields
  - `t_bio_deposit` persists `0..n` bio-deposit rows per case
  - migration is SQLite-safe and idempotent for local upgrade path
- Verification:
  - `ruff check backend/alembic/versions backend/app/modules/cases/models.py`
  - `pytest -q backend/tests/test_case_fields.py -k "foreign_agent or pct or invalidation or bio_deposit"`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing backend tests first
- [ ] Implement migration + model only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
