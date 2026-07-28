# Story V8-CANARY-SCHEMA-SPINE-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: verify the already-integrated V8 Wave-1 schema spine as one current, clean-tree,
  serialized migration chain before any dependent dirty-product adoption.
- Change mode: current verification only; no migration, model, schema or product byte changes.
- Authority: `docs/product/v8/domain-contract.md` data, migration and SQLite rules.
- Dependency supersession: the retired manifest and catalog gates are replaced by the
  independently approved C3 lean governance range and stateless catalog checker.

## Catalog IDs

1. `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
2. `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
3. `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
4. `FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
5. `FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01`
6. `FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`
7. `FPMS-V8-W1-F1-FEE-OBLIGATION-CARRIER-20260712-01`
8. `FPMS-V8-W1-F2-FEE-OBLIGATION-LINE-CARRIER-20260712-01`
9. `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`
10. `FPMS-V8-W1-F4-OBLIGATION-PAYMENT-EVIDENCE-LINK-CARRIER-20260712-01`
11. `FPMS-V8-W1-F5-FEE-REDUCTION-APPROVAL-CARRIER-20260712-01`

## Exact product paths

- `backend/alembic/versions/v8_w1_l1_case_lifecycle_projection.py`
- `backend/alembic/versions/v8_w1_l2_case_activity_event.py`
- `backend/alembic/versions/v8_w1_l3_case_activity_evidence.py`
- `backend/alembic/versions/v8_w1_d1_document_evidence_version.py`
- `backend/alembic/versions/v8_w1_d2_document_evidence_derivation.py`
- `backend/alembic/versions/v8_w1_d3_work_package_evidence_link.py`
- `backend/alembic/versions/v8_w1_f1_fee_obligation.py`
- `backend/alembic/versions/v8_w1_f2_fee_obligation_line.py`
- `backend/alembic/versions/v8_w1_f3_obligation_draft_link.py`
- `backend/alembic/versions/v8_w1_f4_obligation_payment_link.py`
- `backend/alembic/versions/v8_w1_f5_fee_reduction_approval.py`
- `backend/app/modules/cases/models.py`
- `backend/app/modules/documents/models.py`
- `backend/app/modules/official_workflows/models.py`
- `backend/app/modules/fees/models.py`

## Verification

Run the eleven catalog primary tests in ordinal order under the single SQLite/migration
verification lane, then scoped Ruff on those tests and model/migration files. The independent
High reviewer reruns the same decisive tranche on the exact story commit.

## Non-goals and rollback

No dirty archive hunk, new behavior, migration rewrite, backfill, service, API, UI, old
taskctl/evidence mutation, or Foundation claim. Rollback removes only this story record and
its coverage-ledger mapping; existing accepted product bytes remain unchanged.
