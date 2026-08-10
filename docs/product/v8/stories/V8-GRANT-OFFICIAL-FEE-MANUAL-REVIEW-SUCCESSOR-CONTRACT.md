# V8 Grant Official Fee Manual Review Successor Contract

Status: `FROZEN FOR HIGH IMPLEMENTATION`

## Authority

On 2026-08-10 the customer approved方案 A: only an authorized operator, using the archived
and approved grant-notice evidence version, may enter and confirm every official full amount.
The system records operator, time, source document, evidence version/hash, before/after amounts
and idempotency identity before any line changes from `REVIEW_REQUIRED` to `MATCHED`. No rate
book, reduction ratio, payable amount or other value may be used to infer a full amount.

This successor closes only the missing authority prerequisite identified for catalog Row120.
It does not activate an automatic grant-year draft decision or change the generic draft writer.

## Public controlled action

Add one authenticated endpoint:

`POST /grant-fee-tasks/{task_id}/official-fee-review`

- permission: `GrantFeeTask.Write`;
- body: exact source activity, obligation, approved evidence version/hash, naive confirmation
  time, caller idempotency key, and a non-empty ordered list containing every current obligation
  line exactly once;
- each line supplies its exact obligation-line ID, manually entered `official_full_amount`, and
  the notice payable amount being confirmed;
- response: task, obligation, source activity, review activity, reviewed line IDs, confirmation
  time, idempotency key and `reused`.

Money inputs are finite positive two-decimal `Decimal` values within `NUMERIC(18,2)`. The supplied
payable amount must byte-semantically equal the stored notice/source/payable amount; it selects and
confirms the line but never derives the official full amount. The official full amount is accepted
only as the operator's explicit entry.

## Source and lineage validation

Before writing, the service must revalidate the complete accepted chain:

1. exact current grant task and confirmed `GRANT_REGISTRATION_NOTICE_RECORDED` activity;
2. canonical grant-notice snapshot/hash and source document;
3. current `FINAL` + `APPROVED` evidence version, exact content hash and archived activity
   evidence references;
4. one recognized current `GRANT_YEAR_ANNUITY` obligation and one recognition activity;
5. exact complete current line identities and all immutable fields from the notice projection;
6. every line has `official_full_amount=None` and `difference_review_state=REVIEW_REQUIRED`;
7. command lines have the same canonical order and cardinality, with no missing, duplicate,
   foreign, superseded or additional line.

Missing named objects return the existing 404 boundary. Malformed commands return 400. Any
source, evidence, obligation, line-state, ordering, amount or lineage mismatch returns 409 with no
write. No existence detail may weaken the accepted adapter's fail-closed behavior.

## Durable review fact and transition

Append exactly one `FEE` activity of type
`GRANT_YEAR_OFFICIAL_FEE_REVIEW_CONFIRMED`, with unchanged center projection, source activity equal
to the grant-notice activity, `CONFIRMED` status, actor and reviewer equal to the authenticated
operator, and the original two source/evidence references.

Its canonical payload contains only the frozen schema/version, case/task/obligation/source and
evidence identities, evidence hash, confirmation time, fixed review basis, and complete ordered
before/after line snapshots. Before snapshots retain `official_full_amount=null` and
`REVIEW_REQUIRED`; after snapshots contain the entered amount and `MATCHED`, with payable/source
facts unchanged.

Only after the activity append succeeds may compare-and-set updates change every exact line to the
entered full amount and `MATCHED`, setting `updated_by` and `updated_at`. All writes use the caller
transaction; no service commit. A partial or concurrent update fails 409 so caller rollback removes
the activity and every line change.

## Idempotency and draft seam

Exact same-key replay revalidates the stored activity/evidence, payload and current matched lines,
returns `reused=true`, and writes nothing. Same key with drift, a different key after review,
partial matched state, stale evidence, changed amount or changed line identity fails 409.

Expose one internal read validator for Row120. It must prove one exact review activity and current
matched lines still equal its after snapshot. Row120 may call `prepare_draft` only after this
validator succeeds. The review action never creates a draft, fee item, instruction, payment or
second fee activity.

## Files and non-closure

Implementation allowlist:

- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/grant_fees/schemas.py`
- `backend/app/modules/grant_fees/api.py`
- `backend/tests/test_v8_grant_official_fee_manual_review.py`

No schema/migration, rate or reduction calculation, generic writer change, automatic draft,
client-instruction change, lifecycle/legal-state change, UI change, payment, PayList, service fee,
notification or unrelated cleanup.

## Acceptance

Targeted TDD proves public shape, permission injection, full successful transition, activity and
evidence provenance, unchanged payable/source facts, exact replay, dirty transaction rejection,
all command and lineage failures, partial/concurrent CAS rollback, no inference, and the Row120
read seam. Scoped Ruff, exact diff and independent PROTECTED review must pass before adoption.
