# Story V8-CANARY-LIFECYCLE-CORE-EVIDENCE-KIND-ADOPTION

- Risk: `PROTECTED`
- Outcome: adopt the exact quarantined evidence-kind capacity correction while proving the
  lifecycle carrier, append, projection and apply-event seams remain fail-closed.
- Archive source: `6b2ef89da447353380b99853168d4d38aaf9210a`.
- Dependencies: integrated schema canary `38e3e6bc61f20c4c18872dbabe8a19150e56f0ce`.
- Authority: lifecycle, evidence-lineage, migration and SQLite rules in
  `docs/product/v8/domain-contract.md`.

## Catalog IDs

- `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
- `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
- `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`
- `FPMS-V8-LC-CONTRACTS-20260712-01`
- `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
- `FPMS-V8-LC-LEGACY-PROJECTION-20260712-01`
- `FPMS-V8-LC-APPLY-EVENT-SEAM-20260712-01`

The post-catalog evidence-kind capacity correction is also covered explicitly; it does not
invent a catalog row.

## Exact adopted product paths

- `backend/alembic/versions/v8_delta4_evidence_kind_capacity.py`
- `backend/app/modules/cases/lifecycle_activity_service.py`
- `backend/app/modules/cases/models.py`
- `backend/tests/test_v8_lifecycle_evidence_kind_capacity.py`

The story also updates only the obsolete current-head length assertion in
`backend/tests/test_v8_w1_l3_case_activity_evidence.py` from 32 to 64. The original L3
shape and all constraints remain covered; the dedicated successor test proves the widening
is the only physical change.

## Verification

- RED: adopt the archived test first and observe failure before implementation bytes enter.
- GREEN: evidence-kind capacity test plus the seven catalog primary tests above.
- Scoped Ruff and diff-check.
- Serialized SQLite/migration execution.
- Independent High review and decisive rerun on the exact commit.

## Non-goals and rollback

No other lifecycle event, status rule, API, UI, fee, document workflow, backfill, migration,
source activation or adjacent cleanup. Rollback reverts this exact adoption commit; no
forward-only downgrade is executed.
