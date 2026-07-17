# FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `103`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `531`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Create, exactly replay or wholly supersede one obligation header and its non-empty set of
effective lines by the frozen current identity keys, and append/reuse exactly one
`FEE_OBLIGATION_RECOGNIZED` activity with `center_changes={}` in the same caller-owned
transaction. On a recognized SQLite uniqueness race, reread both the activity idempotency
key and every source-event/fee-code/year identity. A real source fact is persisted exactly;
an estimate is never read, promoted or overwritten here.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Implementation Freeze — 2026-07-13

This section is the complete implementation contract for High. It resolves the earlier
readiness blocker without changing the approved V8 fee semantics, adding a rate, inventing
a source document or absorbing a source-specific adapter. The dependency
`FPMS-V8-LC-ACTIVITY-APPEND-20260712-01` must be PASS before High starts this task.

### Exact public callable and transaction boundary

`backend/app/modules/fees/obligation_service.py` exposes exactly this public callable;
helpers remain private:

```python
def recognize_obligation(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    ...
```

- Parameter order, names and annotations are exact. The command/result and every nested
  value are the frozen types from `obligation_contracts.py`; no dictionary, Pydantic or
  second result interface is authorized.
- `transaction` is an existing SQLAlchemy `Session`. The function may use a nested
  savepoint and `flush()`, but must not call outer `commit()`, outer `rollback()` or close
  the session.
- The session must have no pending `new`, `dirty` or `deleted` objects when the function is
  entered. A source activity appended earlier in the same outer transaction is allowed
  because `append_case_activity()` has already flushed it. A dirty entry uses
  `FEE_OBLIGATION_TRANSACTION_DIRTY` (409) before this service writes anything.
- The complete recognition operation—prior-line key release when applicable, one fee
  activity append, one new header and all new lines—runs inside one
  `transaction.begin_nested()` savepoint. Any failure rolls back that savepoint only. The
  outer transaction stays caller-owned and no partial fee/activity/projection mutation may
  remain.
- No public exception, repository, clock, rate provider, retry loop or HTTP seam is added.
  Business failures use the existing `app.core.errors.BusinessError`.

### Frozen command and line validation

Validation is strict and non-coercing. Strings are preserved exactly after validation;
enums use their `.value`; floats are never accepted or converted.

1. `command` must be exactly a `RecognizeFeeObligationCommand`; `fee_domain`,
   `source_status` and every `difference_review_state` must be real members of the frozen
   enums. General type/shape failure is `FEE_OBLIGATION_COMMAND_INVALID` (400) with
   `details.field`.
2. Require non-blank strings within carrier lengths: `case_id`, `source_activity_id`,
   optional `source_document_id` and `actor_id` are at most 36 characters;
   `obligation_type` and each `fee_code` are at most 64; each `fee_name` is at most 256;
   and `idempotency_key` is at most 128. `currency` is exactly three ASCII uppercase
   letters. Invalid currency uses `FEE_OBLIGATION_CURRENCY_INVALID` (400); other general
   string failures use `FEE_OBLIGATION_COMMAND_INVALID` or
   `FEE_OBLIGATION_LINE_INVALID` (400) with the exact field/index in `details`.
3. `due_date` and optional line `source_date` must be `date` but not `datetime`. Every
   amount must be a finite `Decimal`, be non-negative, have no more than two fractional
   digits and fit `Numeric(18, 2)`. `reduction_ratio` must be a finite `Decimal` in the
   closed interval `0..1`, have at most four fractional digits and fit `Numeric(5, 4)`.
   These are storage-safe checks only. This task does not decide whether a ratio is legally
   allowed or evidence-backed; `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01` owns that
   separate rule. Amount/ratio/date failure is `FEE_OBLIGATION_LINE_INVALID` (400).
4. `fee_year_key` must be an `int` but not `bool` in `0..2147483647`; `0` remains the
   explicit non-annual key. It is never inferred from a date, fee name or case.
5. `lines` must be an actual non-empty tuple. Within one command, the persisted identity
   pair `(fee_code, fee_year_key)` must be unique. Repeating that pair—even with an exact
   duplicate snapshot—is `FEE_OBLIGATION_LINE_DUPLICATE` (400). Input tuple order is not
   business identity; validated lines are processed and returned in ascending
   `(fee_code, fee_year_key)` order.
6. `supersedes_obligation_id` and `supersede_reason` must be supplied together or both be
   `None`. The ID is a non-blank string of at most 36 characters; the reason is non-blank
   text and is preserved exactly. An incomplete pair uses
   `FEE_OBLIGATION_SUPERSEDE_PAIR_INVALID` (409).
7. A `GOV` command requires a non-null `source_document_id`; otherwise use
   `FEE_OBLIGATION_GOV_SOURCE_DOCUMENT_REQUIRED` (409). A `SERVICE` command may explicitly
   pass `None`. Neither domain may infer a document from an estimate, a title or a rate.

The service does not recalculate `payable_amount`, infer a missing amount, compare two
amounts, infer a difference state, select a reduction ratio or activate a fee source. Those
are source-adapter/rule responsibilities. It persists the validated explicit snapshots.

### Exact source and case validation order

After all shape validation and before any write, use this exact order:

1. Missing `Case(command.case_id)` is `CASE_NOT_FOUND` (404).
2. Look up an existing case/activity by `(case_id, idempotency_key)` and apply the complete
   replay rules below. A malformed command can never replay successfully, but an exact
   replay remains valid after its source/header later becomes historical.
3. Resolve `source_activity_id` by global activity ID. Missing uses
   `FEE_OBLIGATION_SOURCE_ACTIVITY_NOT_FOUND`; another case uses
   `FEE_OBLIGATION_SOURCE_ACTIVITY_CASE_MISMATCH` (both 409).
4. A source with `confirmation_status=NEEDS_REVIEW` cannot recognize a real obligation and
   uses `FEE_OBLIGATION_SOURCE_NOT_CONFIRMED` (409). `VERIFIED` and `REVIEW_REQUIRED`
   commands require a `CONFIRMED` source activity. `LEGACY_UNVERIFIED` requires a
   `LEGACY_UNVERIFIED` source activity. A mismatch uses the same error. Event-specific
   lane/type/evidence eligibility remains the owning adapter's rule and is not duplicated
   here.
5. If `source_document_id` is non-null, the document must exist and belong to the command
   case. Missing uses `FEE_OBLIGATION_SOURCE_DOCUMENT_NOT_FOUND`; another case uses
   `FEE_OBLIGATION_SOURCE_DOCUMENT_CASE_MISMATCH` (both 409). This generic seam does not
   infer direction, semantic, current evidence version or review state; the source adapter
   must have established those facts before constructing the command.
6. Validate the superseded header/activity and current identities as frozen below.

All 409 validation failures above write nothing and preserve the caller's usable outer
transaction.

### Canonical line identity and activity payload

For every sorted line, compute the effective identity exactly as W1-F2 froze it:

```text
lowercase_hex_sha256(utf8(case_id + "|" + source_activity_id + "|" + fee_code + "|" + str(fee_year_key)))
```

No whitespace normalization, uppercasing, alias mapping or locale conversion is permitted.

The fee activity payload is exactly one JSON object with this logical shape:

```json
{
  "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
  "obligation_id": "<application-generated UUID>",
  "obligation": {
    "actor_id": "<command actor>",
    "case_id": "<command case>",
    "currency": "CNY",
    "due_date": "YYYY-MM-DD or null",
    "fee_domain": "GOV or SERVICE",
    "lines": [
      {
        "difference_review_state": "MATCHED | SOURCE_PENDING | REVIEW_REQUIRED",
        "fee_code": "<exact code>",
        "fee_name": "<exact name>",
        "fee_year_key": 0,
        "official_full_amount": "0.00 or null",
        "payable_amount": "0.00",
        "reduction_ratio": "0.0000",
        "source_amount": "0.00 or null",
        "source_date": "YYYY-MM-DD or null"
      }
    ],
    "obligation_type": "<exact type>",
    "source_activity_id": "<pre-existing source activity>",
    "source_document_id": "<document UUID or null>",
    "source_status": "VERIFIED | REVIEW_REQUIRED | LEGACY_UNVERIFIED",
    "supersede_reason": "<exact reason or null>",
    "supersedes_obligation_id": "<prior UUID or null>"
  }
}
```

- The illustrative values above are not defaults. Every value comes from the validated
  command except the generated `obligation_id` and schema literal.
- Lines are sorted by `(fee_code, fee_year_key)`. Amounts are rendered at exactly two
  decimal places and ratios at exactly four; dates use ISO format; null remains JSON null.
- Serialize exactly with `json.dumps(..., ensure_ascii=False, sort_keys=True,
  separators=(",", ":"), allow_nan=False)`. No estimate, rate ID, rate-book ID, document
  title, display label or hidden metadata is added.
- For recognition-level idempotency, every command field and normalized sorted line is
  canonical identity. `idempotency_key` is stored on the activity rather than repeated in
  the payload. `obligation_id` is result linkage and is excluded when comparing a replay's
  business payload; the stored ID must still be a valid UUID-shaped 36-character string
  that resolves to the stored header.

### Exact fee activity command

For a new obligation, construct exactly one `LifecycleEventCommand` and call
`append_case_activity()` inside the same savepoint:

- `case_id=command.case_id`
- `event_type="FEE_OBLIGATION_RECOGNIZED"`
- `lane=ActivityLane.FEE`
- `effective_at=source_activity.effective_at`
- `occurred_at=source_activity.occurred_at`
- `actor_id=command.actor_id`
- `reviewer_id=source_activity.reviewer_id`
- `idempotency_key=command.idempotency_key`
- `source_activity_id=command.source_activity_id`
- `supersedes_event_id=None` for a new header; for a correction, the exact prior
  recognition activity resolved below
- `payload=<the exact payload object above>`
- `confirmation_status=CONFIRMED` for `source_status=VERIFIED`, `NEEDS_REVIEW` for
  `REVIEW_REQUIRED`, and `LEGACY_UNVERIFIED` for `LEGACY_UNVERIFIED`
- `evidence_refs` is the source activity's complete evidence-link set copied without
  coercion and sorted by the LC append contract. The existing source-activity link is not
  duplicated as a synthetic `EvidenceReference`. An evidence-free source remains an empty
  tuple; source-specific adapters own any mandatory-evidence rule.

Pass the current case projection as both `previous_projection` and `current_projection`,
pass the unchanged `Case.status` as `legacy_case_status`, and pass
`conflict_codes=()`. Thus the fee append is always lane-only and has
`center_changes={}`. Any invalid stored projection/revision is rejected by the frozen LC
append errors; this service never repairs or bypasses it.

### Exact header, line and returned-result construction

For a new recognition, create one application-generated UUID header with:

- copied case/source/document/domain/type/due/currency/source-status facts;
- `obligation_status=RECOGNIZED`, `client_instruction_status=PENDING`,
  `draft_status=NOT_CREATED`, `payment_status=UNPAID`;
- `official_evidence_status=PENDING` for `GOV` and `NOT_APPLICABLE` for `SERVICE`;
- the supplied supersede pair; and
- `created_by=updated_by=command.actor_id`.

Create every sorted line under that one header with its exact command snapshots, computed
current key, source activity and case, and `created_by=updated_by=command.actor_id`. Do not
create a zero-line header, a line under an existing header, a second header, a draft item,
PayList or payment link.

Return `RecognizeFeeObligationResult` exactly as follows:

- `obligation` is the frozen read value populated from the persisted header/lines;
- `statuses.estimate_status=None` and `statuses.pay_list_status=NOT_CREATED` because neither
  fact has a persistence row in this task; the other statuses reflect the header;
- `activity_id` is the new/reused fee activity ID;
- `idempotency_key=command.idempotency_key`;
- `reused=False` only for the new atomic write and `True` only for exact replay; and
- `superseded_obligation_id` is the actual prior ID or `None`.

Result lines remain sorted by `(fee_code, fee_year_key)`. If an exactly replayed obligation
was later superseded, the replay returns its current persisted historical state
(`obligation_status=SUPERSEDED`, `current_identity_key=None`) rather than pretending it is
still effective. Replay never rewrites that historical state.

### Whole-command replay, new, mixed and identity behavior

The unit of idempotency and atomicity is the whole command/header, not an individual line.

- **Exact replay:** after shape and case validation, an existing
  `(case_id, idempotency_key)` must be a `FEE_OBLIGATION_RECOGNIZED` FEE activity whose
  canonical business payload equals the command and whose payload `obligation_id` resolves
  to exactly one same-case header with the expected complete line set. Reconstruct the
  stored fee activity command and call `append_case_activity()` so LC-level activity and
  evidence replay checks also pass. Return that whole stored obligation/activity with
  `reused=True`; add, update and flush nothing.
- **Same key, different fact:** any event type/lane/source/actor/confirmation/evidence,
  canonical business payload, generated-link/header or complete line-set mismatch uses
  `FEE_OBLIGATION_IDEMPOTENCY_CONFLICT` (409) with no write. A malformed stored recognition
  payload/link uses `FEE_OBLIGATION_STORED_STATE_INVALID` (409), never silent repair.
- **New:** with no matching activity and no conflicting effective identity, create the one
  header, all lines and one fee activity atomically.
- **Different key, same identity:** current identity is not an alternate idempotency key.
  Even when every snapshot is equal, it cannot alias an activity carrying another key;
  use `FEE_OBLIGATION_IDENTITY_CONFLICT` (409). This preserves the frozen result's
  idempotency key and prevents duplicate recognition activities.
- **Mixed identity:** for a non-superseding command, if only some requested keys exist or
  the existing keys belong to multiple headers, use
  `FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT` (409). No existing line is reused under a new
  header and no missing line is appended to an existing header.

### Whole-header supersede and current-key rotation

A superseding command is validated only after exact replay has been ruled out:

1. The prior header must exist and belong to the command case; missing uses
   `FEE_OBLIGATION_SUPERSEDED_NOT_FOUND`, another case uses
   `FEE_OBLIGATION_SUPERSEDED_CASE_MISMATCH` (409).
2. It must be `RECOGNIZED`, have at least one line, and every prior line must hold its exact
   non-null current key. It must not already be the parent of another header. Violation is
   `FEE_OBLIGATION_SUPERSEDED_NOT_CURRENT` (409).
3. Prior and new `fee_domain`, `obligation_type` and `currency` must match, and the new
   `source_activity_id` must differ from the prior source. Violation is
   `FEE_OBLIGATION_SUPERSEDE_SCOPE_MISMATCH` (409). Due date, source document, source
   status and the complete line set may change because those are the correction facts.
4. Resolve exactly one prior FEE-lane `FEE_OBLIGATION_RECOGNIZED` activity whose V1 payload
   names the prior header. Missing, duplicate or malformed linkage is
   `FEE_OBLIGATION_PRIOR_ACTIVITY_INVALID` (409). The new fee activity sets
   `supersedes_event_id` to that activity; it never points to the source activity.
5. Inside the savepoint, set the prior header status to `SUPERSEDED`, set all its line
   `current_identity_key` values to `None`, set `updated_by=command.actor_id` and update the
   affected audit timestamps. Flush those rotations before inserting a new line whose key
   could match a released prior key. Then append the correction activity and create the new
   header/lines. A later failure rolls all rotations back with the savepoint.
6. Requested keys that are currently owned by the superseded header are permitted because
   they are released in the same savepoint. Any requested key owned by another effective
   header is `FEE_OBLIGATION_IDENTITY_CONFLICT` (409). There is no partial supersede,
   in-place amount edit or mutation of prior source/audit creation facts.

### SQLite uniqueness-race strategy

Preflight identity reads are advisory; the nullable unique
`t_fee_obligation_line.current_identity_key` and activity `(case_id, idempotency_key)`
constraints remain authoritative.

- Catch only `IntegrityError` attributable to one of those two unique identities from
  inside the nested savepoint. Let the savepoint roll back; never roll back the outer
  transaction.
- Reread the case/activity idempotency row and every requested current line identity once.
  If the stored activity, payload, header and complete line set prove the same whole-command
  replay, return it with `reused=True`.
- A visible same-key mismatch is `FEE_OBLIGATION_IDEMPOTENCY_CONFLICT`; visible same/different
  key line ownership follows the exact identity/mixed errors above. If the competing row is
  not yet visible after the reread, use `FEE_OBLIGATION_CONCURRENCY_CONFLICT` (409) and let
  the caller retry the complete outer transaction.
- Do not swallow a foreign-key, check, type or unclassified integrity failure. Re-raise it;
  masking a schema/programming defect as a business conflict is prohibited. A SQLite
  `database is locked`/driver error is also not converted or retried inside this service.

### Real-source versus estimate and official-rate boundary

- `preview_estimate()` is read-only and has no carrier, activity or ID that this command can
  consume. Recognition never queries an estimate and never turns one into an obligation.
- The source activity/document and explicit line snapshots are the real command facts. A
  source amount, verified official amount and difference state are preserved together;
  this task never silently replaces one with the other. Consequently
  `estimate_status=None` is exact, and “real notice wins over estimate” requires no estimate
  mutation in this seam.
- The frozen command has no rate ID or official-rate-book ID. This service must not query
  `FeeRate`/`OfficialRateBook`, choose a version, activate a source, infer a legal amount or
  claim a synthetic/current CNIPA rate. An upstream rule/adapter supplies the explicit
  snapshots only after its own activation and source checks.
- Therefore generic High implementation is ready once LC append is PASS. Production use by
  official-fee adapters still depends on the separately approved official-rate-book carrier
  and `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`, plus each exact
  source-document/evidence adapter. Those are residual activation/data prerequisites, not
  hidden work in this closure.

### Frozen RED / GREEN dataset

`backend/tests/test_v8_fee_obligation_recognize.py` must use real foreign-key-enabled SQLite
sessions and cover all of the following through the public callable:

1. a verified GOV command with two intentionally unsorted lines creates one header, two
   sorted effective lines, exact current keys and exactly one unchanged-centre fee activity;
2. caller rollback removes header, lines, activity/evidence copies and revision change;
   service commit/outer rollback calls are absent;
3. initial GOV/SERVICE status differences, exact frozen result types and
   `estimate_status=None`/`pay_list_status=NOT_CREATED` are asserted;
4. exact replay, including after a later activity and after later supersede, returns the
   same header/activity with `reused=True` and performs no write;
5. same key with any changed command/line/evidence fact is the exact idempotency 409;
   different key with all, partial or multi-header current identities uses the exact
   identity/mixed 409 and creates no partial header/line/activity;
6. duplicate line pair, empty line tuple, invalid amount/ratio/date/year/currency and an
   incomplete supersede pair fail with the exact status/code and no write;
7. missing/cross-case source activity, unconfirmed source, required/missing/cross-case GOV
   source document and missing case fail in the frozen order with no write;
8. whole-header supersede clears every prior key, marks only the prior obligation status,
   creates the replacement set/activity, links the two recognition activities and rolls all
   changes back if a forced later failure occurs;
9. prior-not-current, scope mismatch, missing/malformed prior activity and a key owned by an
   unrelated header fail closed;
10. simulated recognized unique races prove exact replay recovery, identity/mixed conflict
    and not-yet-visible concurrency conflict while the outer session remains caller-owned;
11. `REVIEW_REQUIRED` and `LEGACY_UNVERIFIED` map to the exact fee activity confirmation,
    source evidence rows are copied exactly, and estimates/rate tables/drafts/PayLists/
    payments are never read or written.

The serialized inherited regression command is:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_fee_obligation_contracts.py \
  tests/test_v8_w1_f1_fee_obligation.py \
  tests/test_v8_w1_f2_fee_obligation_line.py \
  tests/test_v8_lifecycle_activity_append.py
```

### Reaffirmed non-closure

No preview implementation, rate/rate-book lookup or activation, fee-reduction eligibility,
amount arithmetic, source-specific event whitelist, document/evidence review workflow,
client instruction, detail read, draft, PayList, payment, legacy adapter, endpoint, UI,
schema/migration or commit/retry loop. No synthetic official fee source or customer decision
is introduced.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`
- `FPMS-V8-FO-CONTRACTS-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): contracts, append seam

### Shared ownership serialization

- `backend/app/modules/fees/obligation_service.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01.md`
- `backend/app/modules/fees/obligation_service.py`
- `backend/tests/test_v8_fee_obligation_recognize.py`
- `artifacts/FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_recognize.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_recognize.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_contracts.py tests/test_v8_w1_f1_fee_obligation.py tests/test_v8_w1_f2_fee_obligation_line.py tests/test_v8_lifecycle_activity_append.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_recognize.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_recognize.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_recognize.py`
- `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_fee_obligation_recognize.py tasks/postdemo/v8/FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01` pass. Only then may this task be reported PASS.
