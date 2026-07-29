# Story V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the coherent document-evidence service core
  satisfies the five frozen catalog contracts for version registration, derivation
  registration, current-version switching, evidence review and external-submission
  finalization.
- Change mode: current verification only; no product, test, ledger, disposition or review
  byte changes.
- Authority: the document/evidence lineage rules in `docs/product/v8/domain-contract.md`,
  the source-precedence rules in `docs/product/v8/source-decision-registry.md`, and the five
  frozen task contracts named below.
- Dependencies: the current row-42 interface is bound by
  `V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION`; the lifecycle append seam is bound
  by `V8-CANARY-LIFECYCLE-CORE-EVIDENCE-KIND-ADOPTION`.

## Catalog IDs and exact closures

1. `FPMS-V8-DE-REGISTER-VERSION-20260712-01` (ordinal 43): register one immutable version,
   reject wrong-case document/attachment relations, and append its exact `DOCUMENT`
   activity in the caller transaction.
2. `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01` (ordinal 44): register one same-case
   parent-child derivation and append its exact `DOCUMENT` activity in the caller
   transaction.
3. `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01` (ordinal 45): compare-and-swap the current
   working version, preserve exact replay, and reject ordinary replacement of a final
   receipt-linked version.
4. `FPMS-V8-DE-REVIEW-SERVICE-20260712-01` (ordinal 46): record one irreversible
   independently made approve/reject decision, preserve its activity history, and reject a
   rejected target from later current-version promotion.
5. `FPMS-V8-DE-FINALIZE-EXTERNAL-SUBMISSION-SEAM-20260712-01` (ordinal 47): finalize only
   same-case current independently approved final evidence, persist/reuse the exact result,
   and append its `DOCUMENT` activity without a filing/OA lifecycle transition.

## Exact product paths

- `backend/app/modules/documents/evidence_service.py`
- `backend/app/modules/documents/evidence_workflow_service.py`

## Exact task tests

- `backend/tests/test_v8_document_evidence_register_version.py`
- `backend/tests/test_v8_document_evidence_derivation.py`
- `backend/tests/test_v8_document_evidence_current_version.py`
- `backend/tests/test_v8_document_evidence_review_service.py`
- `backend/tests/test_v8_finalize_external_submission_seam.py`

## Narrow inherited regressions

- `backend/tests/test_v8_document_evidence_contracts.py`
- `backend/tests/test_v8_lifecycle_activity_append.py`

These are the only inherited regressions in this story. They prove the exact row-42 value
interface and the caller-owned append seam required by the row 43–47 task contracts.

## Verification

Run the full tranche once under the granted serialized SQLite lane from this worktree's
`backend` directory:

```text
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_document_evidence_contracts.py tests/test_v8_lifecycle_activity_append.py tests/test_v8_document_evidence_register_version.py tests/test_v8_document_evidence_derivation.py tests/test_v8_document_evidence_current_version.py tests/test_v8_document_evidence_review_service.py tests/test_v8_finalize_external_submission_seam.py
```

Run scoped Ruff on the two exact product paths and seven exact tests, then exact
diff-check. The independent High reviewer reruns the same decisive tranche on the exact
story commit.

## Contract and later-hunk boundary

This story consumes without widening the current row-42 boundary: `EvidenceRole` remains
the exact approved twelve-member sequence, `EvidenceDerivationType` remains the original
exact seven-member sequence, and `OA_REPLY_PREPARATION` remains absent.

Archive commit `6b2ef89` is historical input, not current acceptance. Its later OA-reply
and other later-task hunks are deliberately excluded; this story neither imports
`prepare_oa_reply` nor absorbs any row after ordinal 47. Existing successor-owned role,
registration-matrix and external-submission-allowlist behavior in the lean baseline remains
read-only and outside this row 43–47 closure.

## Non-goals and rollback

No OA-reply seam, later derivation value, role change, registration-policy or
external-submission-allowlist change, endpoint, UI, schema/migration, lifecycle transition,
receipt creation, correction override, old taskctl/evidence mutation or Foundation claim.
Rollback removes only this story record and its later coverage-ledger mapping; current
product/test bytes and independently verified dependencies remain unchanged.
