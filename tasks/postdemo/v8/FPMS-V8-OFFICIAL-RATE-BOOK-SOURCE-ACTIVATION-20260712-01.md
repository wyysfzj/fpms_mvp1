# FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-14 / HIGH RACE EVIDENCE ADDED 2026-07-14 / ULTRA CONTRACT FROZEN 2026-07-13
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `157`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `artifacts/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01/analysis/ultra_freeze_proposal.md`
- Source catalog line: `613`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: medium
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Approve and activate one already-persisted `OfficialRateBook` candidate through one atomic
service call, but only after the frozen CNIPA provenance, actor, state, interval and
expected-current validations pass.

## Ultra Contract Freeze — 2026-07-13

This section is the complete High implementation contract for source approval and
activation. It consumes an already-persisted candidate only. Candidate creation/import,
an API, fee amounts and rate rules remain separate closure slices.

### Exact callable and DTOs

```python
activate_official_rate_book(
    command: ActivateOfficialRateBookCommand,
    transaction: Session,
) -> ActivateOfficialRateBookResult
```

`ActivateOfficialRateBookCommand` has exactly:

- `rate_book_id: str`
- `approved_by: str`
- `approved_at: datetime`
- `activated_by: str`
- `activated_at: datetime`
- `expected_current_rate_book_id: str | None`

All IDs are canonical UUID strings. Both datetimes are timezone-naive UTC and
`approved_at <= activated_at`. `approved_by` and `activated_by` may identify the same
active `T_User`; no four-eyes rule or service-layer role policy is invented.

`ActivateOfficialRateBookResult` has exactly:

- `rate_book_id`, `book_code`, `version_code`
- `effective_from`, `effective_to`
- `approval_status`, `activation_status`
- `disposition: ACTIVATED | REUSED`

The persisted row is the durable audit result. The result DTO does not invent a
`supersedes` field absent from the carrier.

### Persisted candidate and exact CNIPA provenance validation

Before any mutation, validate the stored candidate as follows:

- `source_authority == "CNIPA"`; `book_code`, `version_code`, `source_reference` and
  `source_version` are nonblank, already-trimmed exact strings within their carrier limits.
- `source_snapshot` is canonical UTF-8 JSON produced with
  `ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False`; parsing
  and re-serialization must reproduce the exact stored text.
- Its top-level keys are exactly `schema_version` and `sources`,
  `schema_version == "CNIPA_RATE_SOURCE_V1"`, and `sources` is a non-empty list.
- Every source object has exactly `content_sha256`, `document_no`, `published_on`,
  `retrieved_at`, `title` and `url`. All values except `document_no` are nonblank exact
  strings; `document_no` is `None` or a nonblank exact string.
- Every `content_sha256` and the outer `source_snapshot_hash` are lowercase 64-character
  SHA-256 hex. The outer hash must equal
  `sha256(source_snapshot.encode("utf-8")).hexdigest()`. This is the frozen two-level
  content-hash plus canonical-snapshot-hash contract.
- Every URL is canonical HTTPS with host exactly `www.cnipa.gov.cn`, with no credentials,
  explicit port, query or fragment. Customer files, Tianyue and other commercial hosts are
  untrusted. The service performs no network fetch: content hashes are an
  approver-attested snapshot and the outer hash proves stored integrity.
- Every `published_on` is exact `YYYY-MM-DD`; every `retrieved_at` is an RFC-3339 UTC
  timestamp ending `Z`. The first source URL/date exactly match
  `source_reference/source_published_on`.
- `effective_to` is an inclusive end and is absent or `>= effective_from`.

Do not silently expand the trust allowlist. A future CNIPA-adopted external instrument
requires an explicit trust-contract task.

### Actors, state, replay and idempotency

- Both approval and activation actors must exist and be active. They may be the same user;
  API authorization and any future separation-of-duties policy remain outside this service.
- A not-yet-active candidate may be exactly `PENDING/INACTIVE`, or
  `APPROVED/INACTIVE` with approval actor/time exactly equal to the command. `REJECTED`,
  `RETIRED` and every inconsistent approval/activation tuple fail closed.
- For `PENDING/INACTIVE`, this call atomically writes `APPROVED` and the exact approval
  actor/time before activation. For a valid pre-approved row it never rewrites approval
  facts.
- Exact replay against the same already-`ACTIVE` candidate and identical stored
  approval/activation actor/time returns `REUSED` before the current-row CAS check.
- An already-active candidate with differing approval or activation actor/time raises the
  activation-payload conflict. Series/version identity plus the immutable first
  approval/activation tuple is the idempotency identity; do not simulate an absent
  idempotency column.
- Source identity, snapshot/hash, effective interval and first activation actor/time are
  immutable after activation.

### Closed intervals, predecessor CAS and transaction ownership

- Compare intervals within `(source_authority, book_code)` against every other `ACTIVE` or
  `RETIRED` row, not only the current row.
- Intervals are inclusive. Overlap exists when
  `a_from <= (b_to or +infinity)` and `b_from <= (a_to or +infinity)`. Same-day touching
  overlaps; a successor may begin only the day after a closed predecessor.
- Never guess or shorten an official interval. An open-ended predecessor blocks a successor
  until separately verified source data supplies an end date.
- The current-identity CAS is exact: when a current row exists, its ID must equal
  `expected_current_rate_book_id`; when none exists, the expected value must be `None`.
  A mismatch fails before mutation.
- After all validation, retire only that matched predecessor by setting
  `activation_status="RETIRED"`, `current_identity_key=None` and its generic update audit
  actor/time. Preserve its source, approval and first activation facts.
- Activate the candidate with the exact approval/activation facts and
  `current_identity_key="CNIPA|<book_code>"`.
- Perform predecessor retirement and candidate activation in one nested
  transaction/savepoint and call `flush()`. Never call `commit()`, caller-wide
  `rollback()` or `close()`.
- The carrier's unique current key is the final race arbiter. On `IntegrityError`, roll back
  only the savepoint and re-read. Return `REUSED` only if the exact candidate won with the
  identical immutable tuple; otherwise raise the current-identity conflict. Savepoint
  rollback must undo every tentative predecessor retirement.

### Exact error matrix

| HTTP | Code | Exact condition |
| --- | --- | --- |
| 400 | `OFFICIAL_RATE_BOOK_INVALID_INPUT` | wrong command/type, noncanonical UUID or invalid datetime ordering |
| 404 | `OFFICIAL_RATE_BOOK_NOT_FOUND` | candidate absent |
| 404 | `OFFICIAL_RATE_BOOK_ACTOR_NOT_FOUND` | either actor absent |
| 409 | `OFFICIAL_RATE_BOOK_ACTOR_INACTIVE` | either actor inactive |
| 409 | `OFFICIAL_RATE_BOOK_SOURCE_INVALID` | noncanonical, corrupt or hash-mismatched snapshot |
| 409 | `OFFICIAL_RATE_BOOK_SOURCE_UNTRUSTED` | non-CNIPA, customer or commercial source |
| 409 | `OFFICIAL_RATE_BOOK_STATE_CONFLICT` | rejected, retired or inconsistent candidate tuple |
| 409 | `OFFICIAL_RATE_BOOK_ACTIVATION_PAYLOAD_CONFLICT` | active-candidate replay actor/time payload differs |
| 409 | `OFFICIAL_RATE_BOOK_INTERVAL_OVERLAP` | any inclusive `ACTIVE`/`RETIRED` historical or current overlap |
| 409 | `OFFICIAL_RATE_BOOK_CURRENT_IDENTITY_CONFLICT` | expected-current CAS or unique-current race conflict |

Each error exposes only stable IDs and field names. Do not log the source body or customer
data.

### Exact seed boundary

- `seed_official_fee_rate_catalog()` must never create, approve, activate or link a real
  `OfficialRateBook`; its customer/Tianyue constants must never populate
  `FeeRate.official_rate_book_id` or become an activation source.
- Do not convert customer-derived `source_status`, enable a rate, change an
  amount/category or bulk-link catalog rows. Those remain separate rate/rule tasks.
- Until a real CNIPA snapshot, content hashes, version/effective interval and accountable
  approver are supplied and reviewed, development seed contains no auto-approved active
  legal rate-book row. Synthetic CNIPA-host snapshots are permitted only in isolated tests
  and must be labelled synthetic.

### Exact RED/GREEN test contract

`backend/tests/test_v8_official_rate_book_activation.py` must cover exactly these ten parts:

1. RED on the missing callable.
2. A valid `PENDING/INACTIVE` candidate activates; a valid pre-approved candidate
   activates; the same approval/activation actor is accepted; the caller transaction is
   not committed.
3. Exact replay returns `REUSED`; a differing replay payload returns 409.
4. Canonical schema/hash/cross-field validation, malformed JSON, extra/missing keys, empty
   sources, bad hashes/date/timestamp and first-source mismatch.
5. Customer file, Tianyue, non-CNIPA, HTTP, query and fragment sources are rejected with no
   write.
6. Missing/inactive actors and invalid state tuples fail closed.
7. Inclusive same-day overlap and overlap with `RETIRED` history fail; a next-day successor
   succeeds and preserves predecessor source/approval/first-activation facts.
8. Expected-current mismatch and competing candidates produce one active winner, no partial
   retirement and no caller-wide rollback.
9. Seed is idempotent and never creates, activates or links a book from customer sources.
10. The named inherited regressions remain green:
    `tests/test_v8_official_rate_book_schema.py` and
    `tests/test_official_fee_rate_catalog_seed.py`.

## Explicit Non-Closure

No candidate creation/import, endpoint/API/UI/schema, fee amount, fee-rate/rate-rule
implementation, customer-source activation, customer-derived rate enablement/linkage or
adjacent service rule. Do not absorb another V8 catalog row, a second closure slice, an
unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-OFFICIAL-RATE-BOOK-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `backend/tests/test_v8_official_rate_book_schema.py`: read-only carrier regression.
- `inherited` — `backend/tests/test_official_fee_rate_catalog_seed.py`: read-only seed regression.

- Approved source dependency cell (verbatim): carrier

### Shared ownership serialization

- `backend/app/modules/fees/official_rate_book.py`: this activation task is order key `1`;
  `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01` follows it at order key `2`.
  Project this order only across owners present in the active manifest.
- `backend/scripts/seed_dev.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01` — read-only provider and next serialized owner of `backend/app/modules/fees/official_rate_book.py`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01.md`
- `backend/app/modules/fees/official_rate_book.py`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_v8_official_rate_book_activation.py`
- `artifacts/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_official_rate_book_activation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_official_rate_book_activation.py tests/test_v8_official_rate_book_schema.py tests/test_official_fee_rate_catalog_seed.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py scripts/seed_dev.py tests/test_v8_official_rate_book_activation.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py scripts/seed_dev.py tests/test_v8_official_rate_book_activation.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py scripts/seed_dev.py tests/test_v8_official_rate_book_activation.py`
- `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/scripts/seed_dev.py backend/tests/test_v8_official_rate_book_activation.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01` pass. Only then may this task be reported PASS.
