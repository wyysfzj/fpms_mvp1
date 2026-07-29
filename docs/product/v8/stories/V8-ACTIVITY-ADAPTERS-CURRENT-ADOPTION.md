# Story V8-ACTIVITY-ADAPTERS-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: adopt the missing certificate-archive activity adapter and prove the existing
  government-payment activity adapter remains exact on the current lean tree.
- Change mode: minimum row-77 product/test adoption plus row-124 current verification.
- Authority: the lifecycle, official-fee, payment and document/evidence-lineage rules in
  `docs/product/v8/domain-contract.md`; the source and customer-decision fail-closed rules
  in `docs/product/v8/source-decision-registry.md`; frozen catalog rows `77` and `124`;
  and their exact task contracts.
- Archive comparison anchor:
  `6b2ef89da447353380b99853168d4d38aaf9210a`.
- Base: `11cc8025c0362ce720f92a508bc05626ff22d683`.

## Catalog IDs and dependencies

1. `FPMS-V8-CERTIFICATE-ARCHIVED-ACTIVITY-20260712-01` (ordinal `77`,
   profile `TC-ADAPTER`) depends on:
   - `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`, current-verified by
     `V8-CANARY-LIFECYCLE-CORE-EVIDENCE-KIND-ADOPTION` at
     `7bb54cef0d4f8d7c10c177be54b1adddc01e1d06`; and
   - `FPMS-V8-DE-REGISTER-VERSION-20260712-01`, current-verified by
     `V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION` at
     `6672d239e4f0aa7c0575ad5392987ef954140f0f`.
2. `FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01` (ordinal `124`,
   profile `TC-ADAPTER`) depends on
   `FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01`, current-verified by
   `V8-FEE-OBLIGATION-CORE-CURRENT-VERIFICATION` at
   `f89d222861d6ebda88ead322cfd7254e8fb26e64`.

## Exact row-77 adoption

The current `add_attachment` entrypoint now recognizes only the frozen patent-certificate
template identity: exact code `OFFICIAL_NOTICE_010`, catalog kind `OFFICIAL_NOTICE`, and
official notice name `专利证书`. After registering the immutable attachment evidence
version, it appends exactly one confirmed `CERTIFICATE_ARCHIVED` `DOCUMENT` activity in
the same caller transaction.

The activity reuses the evidence version's creation timestamp and creator, preserves the
case's existing lifecycle projection on both sides, carries the exact attachment,
document and evidence-version identities, and links the exact
`DocumentEvidenceVersion` content hash as lifecycle evidence. Its idempotency identity is
`certificate-archived:{evidence_version_id}`.

This activity does not change the grant effective date, legacy case status, business
stage, official-procedure stage or legal status. It does not infer that certificate
attachment grants the patent or create a second entrypoint.

## Exact row-124 current boundary

The row-124 focused test is byte-identical to the archive checkpoint, and the owned
`register_gov_payment` payment-evidence/activity block is unchanged. Registration links
the exact payment to the exact obligation lines and appends one `PAYMENT_RECORDED` `FEE`
activity using the deep payment-evidence seam and lifecycle append identity.

The activity preserves the obligation's source-activity identity and unchanged lifecycle
projection. It neither duplicates the financial activity nor treats payment as verified
official receipt evidence. The adjacent row-125 official-evidence successor remains
outside this story and is not imported from the archive.

## Exact paths

### Product

- `backend/app/modules/documents/service.py`
- `backend/app/modules/annuity/service.py` (verified unchanged)

### Focused tests

- `backend/tests/test_v8_certificate_archived_activity.py`
- `backend/tests/test_v8_gov_payment_activity_adapter.py` (verified unchanged)

### Story

- `docs/product/v8/stories/V8-ACTIVITY-ADAPTERS-CURRENT-ADOPTION.md`

## RED, GREEN and review

Under the controller-granted serialized SQLite/shared lane:

- row 77 RED: `1 failed, 2 warnings`; the evidence-version activity existed, but the case
  lifecycle revision was `1` instead of `2` because `CERTIFICATE_ARCHIVED` was missing;
- row 77 GREEN after the minimum adapter change: `1 passed, 2 warnings`; and
- row 124 untouched current verification: `1 passed, 1 warning`.

The warnings are existing third-party passlib and Pydantic deprecations. The lane was
released immediately after the two focused GREEN runs.

Run scoped Ruff check-only on the two exact product/test pairs, exact-range diff-check,
and inspect the commit file list. An independent High reviewer must review the exact
commit and independently rerun both focused tests under the serialized lane. The
implementer does not approve this `PROTECTED` story; it remains pending independent
review.

## Non-goals and rollback

No deep lifecycle or evidence rule change, second document or payment entrypoint, grant
effective-date or legal-status inference, official receipt verification, fee amount or
source activation, duplicate activity, endpoint/API/UI, schema/migration/seed, unrelated
shared-service successor, customer-decision activation, ledger/disposition/review edit,
old task/evidence mutation or Foundation claim.

Rollback reverts the story card, row-77 focused test and row-77 certificate activity hook.
The already-integrated row-124 product and test bytes remain unchanged.
