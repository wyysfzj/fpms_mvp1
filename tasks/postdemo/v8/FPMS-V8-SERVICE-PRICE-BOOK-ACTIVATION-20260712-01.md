# FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `226`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `734`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-SERVICE-RATE-VERSION[GLOBAL]`

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

Activate one populated, approved, non-overlapping DRAFT version; empty/malformed snapshots are 409.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-SERVICE-RATE-VERSION:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell (verbatim): import service; serialized

### Shared ownership serialization

- `backend/app/modules/fees/service_price_book.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01.md`
- `backend/app/modules/fees/service_price_book.py`
- `backend/tests/test_v8_service_price_book_activation.py`
- `artifacts/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Require the exact persisted gate and lane activation; absent/revoked/future/scope-mismatched decisions are 409/no write.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_service_price_book_activation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_service_price_book_activation.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/service_price_book.py tests/test_v8_service_price_book_activation.py && .venv/bin/ruff format app/modules/fees/service_price_book.py tests/test_v8_service_price_book_activation.py && .venv/bin/ruff check app/modules/fees/service_price_book.py tests/test_v8_service_price_book_activation.py`
- `git diff --check -- backend/app/modules/fees/service_price_book.py backend/tests/test_v8_service_price_book_activation.py tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01` pass. Only then may this task be reported PASS.

## Latest-Wins Input Activation Dependency Interpretation

Development prerequisite: adopted successor + exact code dependencies.
Production prerequisite: original DG-* gate plus reviewed active real input.
Missing production input: 409 / NO WRITE; does not block RED/GREEN or CAPABILITY_READY.
Existing closure, non-closure, allowlist, permissions, primary tests and evidence remain intact.

## Frozen Activation Service Contract (2026-08-13)

- The exact entry point is
  `activate_service_price_book(transaction, ActivateServicePriceBookCommand(...))`.  The frozen
  command contains `price_book_id`, `approval_reason`, `actor_id`, `at`,
  `expected_current_price_book_id`, and server-derived `runtime_profile`.  The service never
  commits or rolls back the caller-owned transaction.
- One authenticated actor approves and activates the candidate atomically.  That actor must be a
  persisted active user and must differ from the draft `created_by`; approval and activation are
  recorded with the same actor/time.  This is the row's independent approval boundary; there is
  no second review endpoint or hidden approval state in this closure.
- Only a `PRODUCTION` draft may become `ACTIVE`, and only outside the `test` runtime profile.
  `TEST_ONLY` drafts and production activation from the test profile return
  `SERVICE_PRICE_BOOK_ACTIVATION_CONFLICT` / `409` with no mutation.  This prevents test fixtures
  from occupying the production `GLOBAL` current identity.
- Before mutation, the service validates the stored source hashes, canonical item snapshot,
  snapshot hash, exact header values, positive item count, effective interval, untouched DRAFT
  tuple, and approval/activation/retirement/lineage tuple.  Empty, malformed, non-canonical or
  hash/count-inconsistent input returns `409` with no mutation.
- Production activation resolves the current effective persisted
  `DG-SERVICE-RATE-VERSION:GLOBAL` decision at `at`.  Its `source_reference` and `source_version`
  must equal the candidate `source_reference` and `book_version`.  Its `decision_value` must be
  the exact canonical JSON object below (UTF-8, sorted keys, compact separators, no NaN):

  `{"book_version":"...","currency":"...","discount_policy":"...","effective_from":"YYYY-MM-DDTHH:MM:SS.ffffff","effective_to":null,"item_count":1,"item_snapshot_hash":"...","scope_key":"GLOBAL","source_content_hash":"...","source_reference":"...","tax_policy":"..."}`

  The real candidate values replace the examples, and a non-null `effective_to` uses the same
  microsecond ISO form.  Missing, revoked, future, corrupt, scope-mismatched or tuple-mismatched
  decisions return `409` with no mutation.
- `expected_current_price_book_id` is a compare-and-set precondition.  It must be `None` when no
  current `GLOBAL` row exists and must exactly identify the sole current row otherwise.
  Multiplicity, a mismatched expectation or corrupt current row is `409` / no write.
- A predecessor may be replaced only when it is a valid `PRODUCTION` `ACTIVE` current row and its
  effective interval does not overlap the candidate (`predecessor.effective_to <=
  candidate.effective_from`).  It is atomically changed to `RETIRED`, loses the current identity,
  records the activation actor/time and a deterministic replacement reason, and becomes the
  candidate's `supersedes_price_book_id`.  Any overlap is `409` / no write.
- The candidate atomically records `approved_by/approved_at/approval_reason`,
  `activated_by/activated_at`, `status=ACTIVE`, `current_identity_key=GLOBAL`, and its predecessor
  lineage.  An exact replay of these durable fields returns disposition `REUSED`; every differing
  replay conflicts.  A first activation returns `ACTIVATED`.
- The result exposes the activated row identity, source classification, version/scope, source and
  item hashes/count, status/effective interval, approval/activation/current/predecessor lineage,
  and `ACTIVATED|REUSED`; it does not quote, create a receivable, expose an endpoint, or infer an
  official fee.
