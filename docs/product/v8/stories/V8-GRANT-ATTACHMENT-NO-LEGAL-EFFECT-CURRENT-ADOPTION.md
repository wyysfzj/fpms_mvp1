# Story V8-GRANT-ATTACHMENT-NO-LEGAL-EFFECT-CURRENT-ADOPTION

- Status: `READY_FOR_INDEPENDENT_REVIEW`.
- Risk: `PROTECTED`.
- Catalog ID: `FPMS-V8-GRANT-ATTACHMENT-NO-GRANTED-20260712-01` (ordinal `75`).
- Product/test commits: `541d25397bd285985b14b4b5c6a09feca15e5cbd` and review
  correction `0b54fe9fc884fe22fc0e5deb5aeea2be923149b6`.
- Parent: `0a9b8b92e65c883995f0f54144023fad3ebc14b5`.
- Authority: frozen Row75 task, the current-verified Row74 dedicated grant-notice
  lifecycle adapter, and the lifecycle-neutral ordinary document/upload contract.

## Exact outcome and scope

Uploading an attachment to a `GRANT_NOTICE` document still creates the grant-fee task,
attachment and initial evidence version in the caller transaction. It no longer writes
legacy `Case.status = GRANTED`, validates grant-ready case fields, or otherwise infers a
legal-state transition. The evidence registration correctly retains its one existing
`DOCUMENT_EVIDENCE_VERSION_REGISTERED` DOCUMENT activity, so the shared revision advances
by one while all three central state axes and the legacy status stay unchanged. The
existing private orchestration seam name is retained so the current-verified Row74
dependency and its focused test remain source-compatible.

Exact product/test paths:

- `backend/app/modules/documents/service.py`
- `backend/tests/test_v8_grant_attachment_no_legal_effect.py`

No dedicated grant lifecycle dispatch, evidence approval, fee amount, deadline lineage,
API/UI, schema/migration, second attachment entrypoint or adjacent document behavior is
changed.

## TDD and verification

- real RED: `1 failed`; after a valid grant-notice attachment upload, expected
  `GRANT_PENDING` but the old side effect stored `GRANTED`;
- focused GREEN: `1 passed`;
- first independent review requested full central-projection and activity assertions;
  the test-only correction proves unchanged central/legacy state and exactly one existing
  DOCUMENT evidence-registration activity rather than incorrectly requiring zero
  activities;
- current Row74 API/dispatcher dependency plus corrected Row75 focused tranche:
  `74 passed`;
- scoped Ruff check and exact diff-check: PASS;
- Ruff format-check reports only the pre-existing Row61 two-literal formatting baseline
  at the unchanged `documents/service.py` impact-preview message; no Row75-owned hunk is
  unformatted.

Independent High re-review must inspect `541d253` and `0b54fe9`, rerun the exact Row75
focused test plus the Row74 two-file dependency tranche under the serialized SQLite lane,
and approve with P0/P1/P2 zero before ledger adoption.

## Rollback

Rollback reverts only `541d253` and this story. It restores the obsolete attachment-driven
legacy status write and therefore must not be used after Row75 adoption without explicitly
reopening the legal-state contract.
