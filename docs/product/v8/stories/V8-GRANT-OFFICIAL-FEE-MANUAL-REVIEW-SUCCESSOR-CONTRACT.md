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

- permission dependency: `GrantFeeTask.Write`; actor is injected only from `current_user.id` and is
  not accepted in the request body;
- path `task_id`: strict non-blank trimmed string, maximum 36 characters;
- request model uses `extra="forbid"` and contains exactly:
  `source_activity_id: str`, `obligation_id: str`,
  `reviewed_evidence_version_id: str`, `expected_content_hash: str`,
  `confirmed_at: datetime`, `idempotency_key: str`, and
  `lines: list[GrantOfficialFeeReviewLineIn]`;
- every request string is strict, non-blank, trimmed and NUL-free. IDs have maximum 36 characters,
  the idempotency key maximum 128, and `expected_content_hash` exactly matches
  `sha256:[0-9a-f]{64}`. `confirmed_at` is naive. `lines` is non-empty;
- line model also uses `extra="forbid"` and contains exactly
  `obligation_line_id: str`, `official_full_amount: Decimal`, and
  `confirmed_payable_amount: Decimal`; line IDs obey the same ID rule;
- the exact response model uses `extra="forbid"` and contains only
  `grant_fee_task_id: str`, `fee_obligation_id: str`, `source_activity_id: str`,
  `review_activity_id: str`, `reviewed_line_ids: list[str]` in canonical order,
  `confirmed_at: datetime`, `idempotency_key: str`, and `reused: bool`; all response IDs and the
  key preserve the validated request/stored values and the time is the exact naive request time;
- success is HTTP 200 with that response as the direct JSON body, without an envelope.

Pydantic request-shape, missing/extra field, type, ID/hash pattern, list cardinality, decimal range
and timezone violations return the existing FastAPI HTTP 422 validation body. Service command-type,
whitespace/NUL or other defensive shape violations return
`GRANT_OFFICIAL_FEE_REVIEW_COMMAND_INVALID` HTTP 400 with the exact invalid field in details.
The service error contract is exact: missing named task is
`GRANT_OFFICIAL_FEE_REVIEW_TASK_NOT_FOUND` HTTP 404; missing named source, evidence, obligation,
line or recognition object is `GRANT_OFFICIAL_FEE_REVIEW_LINK_NOT_FOUND` HTTP 404; dirty caller
transaction is `GRANT_OFFICIAL_FEE_REVIEW_TRANSACTION_CONFLICT` HTTP 409; source/evidence/
obligation/lineage or immutable-fact mismatch is `GRANT_OFFICIAL_FEE_REVIEW_LINEAGE_CONFLICT`
HTTP 409; already/partially reviewed state or a new key after review is
`GRANT_OFFICIAL_FEE_REVIEW_STATE_CONFLICT` HTTP 409; same-key drift or corrupt replay is
`GRANT_OFFICIAL_FEE_REVIEW_IDEMPOTENCY_CONFLICT` HTTP 409; failed CAS is
`GRANT_OFFICIAL_FEE_REVIEW_CONCURRENCY_CONFLICT` HTTP 409. These errors carry no details except
the HTTP 400 command-invalid field described above, and disclose no additional object existence.

Money inputs are finite positive two-decimal `Decimal` values no greater than
`9999999999999999.99` (`NUMERIC(18,2)`). The supplied payable amount must be exactly Decimal-equal
to both stored notice `source_amount` and `payable_amount`; it selects and confirms the line but
never derives the official full amount. The official full amount is accepted only as the operator's
explicit entry.

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

Its payload is canonical JSON (`ensure_ascii=false`, sorted keys, compact separators, NaN denied)
with exactly these top-level keys and JSON types:

- `schema: "FPMS_GRANT_YEAR_OFFICIAL_FEE_REVIEW_CONFIRMED_V1"`;
- `case_id`, `grant_fee_task_id`, `obligation_id`, `source_activity_id`,
  `source_document_id`, `reviewed_evidence_version_id`, `reviewed_evidence_content_hash`: strings;
- `confirmed_at`: the exact naive request time serialized by `datetime.isoformat()`;
- `review_basis: "AUTHORIZED_OPERATOR_MANUAL_ENTRY"`;
- `before_lines` and `after_lines`: non-empty arrays in ascending `(fee_year_key, fee_code,
  obligation_line_id)` order.

Every line snapshot contains exactly: `obligation_line_id: str`, `fee_code: str`,
`fee_name: str`, `fee_year_key: int`, `official_full_amount: str|null`,
`reduction_ratio: str`, `payable_amount: str`, `source_amount: str`,
`source_date: str|null`, `difference_review_state: str`, and `current_identity_key: str`.
Money strings use fixed two decimals; reduction-ratio strings use fixed four decimals; source dates
use ISO `YYYY-MM-DD`. Before snapshots have `official_full_amount=null` and
`difference_review_state="REVIEW_REQUIRED"`; after snapshots differ only in the manually entered
two-decimal `official_full_amount` and `difference_review_state="MATCHED"`. Row120 and replay compare
the decoded object for this exact key set, types, order and values and also require re-encoding to
equal the stored canonical bytes.

`confirmed_at` is used unchanged for activity `occurred_at`, activity `effective_at`, canonical
payload confirmation time, and every updated line's `updated_at`. Activity actor and reviewer are
both the injected current user.

Only after the activity append succeeds may compare-and-set updates change every exact line to the
entered full amount and `MATCHED`, setting `updated_by` and `updated_at`. All writes use the caller
transaction; no service commit. A partial or concurrent update fails 409 so caller rollback removes
the activity and every line change.

Each line CAS predicate is exactly: line `id`, `obligation_id`, `case_id`, `source_activity_id`,
`fee_code`, `fee_name`, `fee_year_key`, `current_identity_key`, `reduction_ratio`, `payable_amount`,
`source_amount`, `source_date`, the previously read `updated_at`, `official_full_amount IS NULL`, and
`difference_review_state = REVIEW_REQUIRED` equal their already validated pre-review values. Each
update must report `rowcount == 1`; any other rowcount is the exact concurrency error above. The
endpoint wraps service invocation and `db.commit()` in one `try`; every exception calls
`db.rollback()` and is re-raised.

## Idempotency and draft seam

Idempotency uses the existing activity store's exact `(case_id, idempotency_key)` scope. Exact
same-key replay is resolved before the pre-review-only state check, then revalidates the stored
activity/evidence, exact command-derived payload and current matched lines, returns `reused=true`,
and writes nothing. Same key with drift, a different key after review, partial matched state, stale
evidence, changed amount or changed line identity fails 409. A same key on another case remains a
distinct activity identity under the existing store constraint.

Expose one internal read validator for Row120. It must prove one exact review activity and current
matched lines still equal its after snapshot. Row120 may call `prepare_draft` only after this
validator succeeds. The review action never creates a draft, fee item, instruction, payment or
second fee activity.

The accepted generic obligation detail/overlay reader remains valid after review. Its recognition
payload stays immutable at the original `null`/`REVIEW_REQUIRED` facts. Only for a current
`GRANT_YEAR_ANNUITY` obligation may the reader reconcile different live line values, and only when
one exact confirmed review activity proves that its `before_lines` equal the recognition facts and
its `after_lines` equal every current line. The activity must retain the exact source activity,
actor/reviewer, canonical payload and original two evidence references. Missing, multiple, corrupt,
partial or unrelated review facts keep the existing `FEE_OBLIGATION_STORED_STATE_INVALID` boundary.
No other obligation type or line transition is generalized.

Review replay uses the review activity's stored old/new lifecycle projection, not the later current
case projection. A legitimate later lifecycle event therefore cannot invalidate exact same-key
review replay or the Row120 read validator.

The existing explicit client-instruction adapter remains order-independent with this review: it
accepts either the original exact `REVIEW_REQUIRED` projection or the exact validated review fact
and current `MATCHED` projection. It still writes only the explicit `PAY`/`HOLD`/`ABANDON`
instruction through the generic writer; no review may imply a client decision.

## Files and non-closure

Implementation allowlist:

- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/grant_fees/schemas.py`
- `backend/app/modules/grant_fees/api.py`
- `backend/app/modules/fees/obligation_service.py`
- `backend/tests/test_v8_grant_official_fee_manual_review.py`

No schema/migration, rate or reduction calculation, generic writer change, automatic draft,
client-instruction change, lifecycle/legal-state change, UI change, payment, PayList, service fee,
notification or unrelated cleanup.

## Acceptance

Targeted TDD proves public shape, permission injection, full successful transition, activity and
evidence provenance, unchanged payable/source facts, exact replay, dirty transaction rejection,
all command and lineage failures, partial/concurrent CAS rollback, no inference, and the Row120
read seam. Scoped Ruff, exact diff and independent PROTECTED review must pass before adoption.
