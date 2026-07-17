# FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01` (`V8`)
Wave: `M5 — foundation external prerequisites`
Phase: `foundation_external_prerequisite` (outside the immutable baseline)
Executor role: Tester / monitor

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-13-fpms-v8-ultra-contract-materialization.md`
- `tasks/postdemo/v8/FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01.md`
- Materialization row: `14`
- Expected manifest phase: `foundation_external_prerequisite`
- Immutable baseline membership: `outside`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: After the strict V8 HTTP adapter is PASS, the unchanged legacy test
  fails because it sends `trigger_event`, omits the explicit effective date, seeds
  unlinked `FeeRate` rows and asserts the removed legacy response.
- GREEN expectation: The one migrated test file passes against the strict V8 request,
  verified linked provider fixtures, direct `FeeEstimate` response and fail-closed
  no-fallback boundary without changing product code.

## Exact Closure Slice

Migrate only `backend/tests/test_official_fee_preview_api.py` from its obsolete legacy
request, unlinked-rate fixture and legacy response expectations to regression tests for
the already-PASS strict V8 official-fee preview HTTP contract.

## Ultra Contract Freeze — 2026-07-13

This task is a test-semantic migration after the HTTP adapter, not a product behavior
task. High may rewrite helpers and assertions inside the one legacy test file only when
each changed line is necessary to replace a superseded assumption listed below.

### Fixed execution precondition and boundary

- `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01` must have accepted PASS evidence and a
  passing task gate before RED is captured for this task.
- Run the unchanged legacy test file against that strict adapter first. Its failures on
  the old request/provider/response assumptions are the required RED; a missing route,
  missing provider or unrelated product failure is not an acceptable RED.
- Do not preserve an old assertion by introducing an alias, coercion, default, legacy
  envelope or fallback in product code. The strict HTTP task remains authoritative.
- The migrated tests use the existing POST path and public HTTP interface only. They do
  not call `preview_estimate()` or the provider directly and do not duplicate provider
  selection or fee-reduction unit tests.

### Exact strict request used by migrated success/error tests

Every request intended to enter the handler has exactly this shape:

```json
{
  "case_id": "<existing case id>",
  "trigger_context": {
    "trigger": "FILING_ACCEPTED",
    "source_document_id": "DOC-OFP-1"
  },
  "currency": "CNY",
  "rate_effective_on": "2026-07-13"
}
```

- Use the fixed test date `date(2026, 7, 13)` and its exact ISO JSON string. Remove
  `date.today()`, `timedelta` relative to today and every implicit-date expectation.
- For reexamination, change only the nested `trigger` to `REEXAM_REQUESTED` and use
  source document `DOC-REJECTION-1`.
- For the unsupported-trigger regression, change only the nested `trigger` to
  `RESTORE_RIGHT_REQUESTED`; the response is HTTP 400 with exact error code
  `FEE_ESTIMATE_TRIGGER_UNSUPPORTED`.
- `trigger_context.source_document_id` remains present in every strict request. Use JSON
  null in the effective-date selection case and a non-null string in the filing and
  reexamination source-echo cases.
- Do not send top-level `trigger_event` or top-level `source_document_id` in any request
  expected to enter the handler.

### Exact verified fixture migration

Replace the unlinked `FeeRate` helpers with deterministic, test-local fixtures satisfying
the already-frozen activation and provider contracts:

1. Create exactly one trusted CNIPA `OfficialRateBook` whose source snapshot/hash are
   canonical and valid, whose approval and activation tuples are complete, whose current
   identity key is `CNIPA|<book_code>`, and whose inclusive interval contains
   `2026-07-13`.
2. Link every admitted synthetic GOV/CNY `FeeRate` through
   `official_rate_book_id == rate_book.id`; use exact provider calc modes, inclusive
   effective intervals and deterministic IDs. The filing fixture supplies the four
   existing codes in provider order; the reexamination fixture supplies the exact INV
   reexamination code.
3. Set the migrated case fixture's explicit `fee_reduction` to string `"0"`. This keeps
   this test focused on HTTP/provider integration and makes the expected ratio
   `"0.0000"`; approved `0.7/0.85` behavior remains owned by provider and pure-preview
   tests. Do not create or infer a reduction approval in this task.
4. Keep one deliberately enabled but unlinked legacy `FeeRate` with a different amount
   in the renamed no-fallback regression. Assert that its ID and amount do not appear,
   while every returned source has `status == "VERIFIED"` and identifies the linked rate
   and rate-book provenance.
5. Treat every amount as a synthetic regression fixture, not an activated legal rate.
   Assertions derive money from the fixture and verify the strict serialization rather
   than claiming a current CNIPA amount.

All fixture writes finish before the before/after request snapshot. Fixture setup is not
part of the endpoint no-write assertion. The test must not invoke an activation service,
seed routine, network fetch or system clock.

### Exact direct-response migration

Replace every legacy response assertion with the direct V8 projection frozen by the HTTP
adapter:

- top-level keys are exactly `case_id`, `estimate_status`, `trigger_context`, `currency`,
  `candidates`, and `total_payable_amount`;
- `estimate_status == "ESTIMATE"`, `currency == "CNY"`, and `trigger_context` exactly
  echoes the strict nested request;
- each candidate has exactly `line` and `source`; line/source keys match the HTTP adapter
  contract, and candidate array order is preserved rather than converted to a dict;
- all money values are fixed two-decimal strings, every reduction ratio is a fixed
  four-decimal string, and each non-null source date is `"2026-07-13"`;
- filing returns the four linked provider candidates in exact order; reexamination
  returns only `CN_REEXAM_FEE_INV`; totals equal the sum of the serialized payable lines;
- no response contains legacy `trigger_event`, top-level `source_document_id`,
  `idempotency_key`, `preview_only`, `draft_type`, `total_gov`, `fee_type`, `quantity`,
  `unit_price`, `amount`, `amount_before_reduction`, `payable_ratio`, `trigger_rule`,
  `deadline_rule`, `fee_category`, `fee_subtype`, `reduction_scope` or legacy
  `source_status` fields.

### Frozen migrated regression matrix

The one file retains the intent of its existing five regressions and adds only the
explicit legacy-shape boundary required by this migration:

1. Filing preview uses the strict request and verified linked candidates, returns the
   exact direct projection and writes no business row.
2. Effective-date selection uses the fixed explicit date and proves an expired/future
   linked rate cannot replace the single rate effective on that date; it never reads the
   process date.
3. The former pending-confirmation regression becomes a verified-link/no-fallback
   regression: an enabled unlinked legacy row is never selected and no unverified source
   is returned.
4. Reexamination uses the strict request, returns the one exact INV candidate and writes
   no business row.
5. A strict request with `RESTORE_RIGHT_REQUESTED` returns 400 and exact code
   `FEE_ESTIMATE_TRIGGER_UNSUPPORTED`.
6. The complete old top-level `trigger_event`/`source_document_id` request returns 422.
   A spy on the legacy `fees.service.preview_official_fee_candidates` seam remains
   uncalled, proving validation does not enter a compatibility or fallback path.

Before each migrated endpoint call, capture counts for `FeeDraft`, `FeeItem`,
`FeeObligation`, `FeeObligationLine`, `FeeObligationPaymentEvidenceLink`,
`CaseActivityEvent`, `PayList`, `GovPayment`, `Payment` and `PaymentLine`. After each 200,
400 or 422 response, assert the exact count tuple is unchanged. The tests also fail on a
handler `flush`, `commit` or `rollback`; SQLite-writing fixture setup and verification run
through the global serialized queue.

### Frozen RED / GREEN sequence

1. Confirm the HTTP-adapter dependency is PASS.
2. Run the unchanged legacy file and retain the expected strict-contract failures as RED.
3. Change only the allowlisted test file to the six migrated regressions above.
4. Run the one file to GREEN, then run scoped Ruff, scope/diff, independent review, task
   gate and atomic evidence validation.

GREEN is only the semantically migrated legacy test file. It is not authorization to
change the route, schemas, provider, service, models, migrations, seeds or another test.

## Explicit Non-Closure

No product source, schema, migration, seed, router, API, service, provider, model, UI or
backward-compatibility change. Do not weaken or delete strict 422/no-fallback behavior,
restore the legacy response, change the already-PASS V8 HTTP/provider tests, duplicate
provider approval/rate-rule coverage, update legal rates, absorb Foundation close or
perform unrelated test cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01` — must be accepted `PASS` before this
  task captures RED or edits the legacy test.

### External, gate and inherited prerequisites

- The HTTP dependency transitively requires the production estimate provider and pure
  preview service; this task adds no independent product dependency or customer gate.
- Customer gate: `None`.

### Shared ownership serialization

- Execute after the strict HTTP adapter; never run concurrently with an owner editing
  `backend/tests/test_official_fee_preview_api.py`.
- All fixture-writing SQLite tests run through the global serialized verification queue.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FOUNDATION-CLOSE-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01.md`
- `backend/tests/test_official_fee_preview_api.py`
- `artifacts/FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01/**`

No product source, schema, migration, seed, router, shared ownership file, other test,
task, manifest or catalog file is authorized. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve the strict V8 direct-response, error-code and no-write contracts already
  frozen by the HTTP adapter; tests may observe them but may not redefine them.
- All dates are fixed explicit test data; no system-clock dependence or external network
  access is permitted.
- Fixture setup uses SQLite-safe caller-owned sessions and commits only fixture rows
  before request snapshots. The endpoint remains read-only.

## Verification Commands

- Dependency gate: `./scripts/task_validate.sh FPMS-V8-FO-PREVIEW-HTTP-ADAPTER-20260712-01`
- RED: `cd backend && .venv/bin/pytest -q tests/test_official_fee_preview_api.py`; run
  before editing and preserve failures caused by the old shape/unlinked fixtures/legacy
  response against the already-PASS strict HTTP adapter.
- GREEN: `cd backend && .venv/bin/pytest -q tests/test_official_fee_preview_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_official_fee_preview_api.py && .venv/bin/ruff format tests/test_official_fee_preview_api.py && .venv/bin/ruff check tests/test_official_fee_preview_api.py`
- Scoped diff: `git diff --check -- backend/tests/test_official_fee_preview_api.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01.md`
- Task gate: `./scripts/task_validate.sh FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01`
- Evidence gate: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `200` for strict filing/reexamination previews, `400` for the
strict unsupported trigger, and `422` for the obsolete legacy request shape.

## Evidence Path

- `artifacts/FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus
  `baseline_allowlist.diff` and `baseline_external_files.txt` when the worktree is dirty.

## Done Definition

The HTTP dependency is accepted PASS; the exact legacy-contract RED is preserved; the
minimum one-file test migration makes all six strict regressions GREEN; scoped Ruff and
diff checks pass; SQLite verification is serialized; baseline-subtracted scope evidence
proves no product or second closure changed; an independent reviewer approves the exact
test migration and non-closure; task and atomic evidence gates pass. Only then may the
implementation task be reported PASS.
