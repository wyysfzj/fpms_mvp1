# FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01

Status: IMPLEMENTED / AWAITING INDEPENDENT REVIEW
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `224`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `docs/product/v8/reviews/V8-INPUT-ACTIVATION-DECOUPLING-CURRENT-ADOPTION.md`
- Source catalog line: `732`
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

Create/reuse one DRAFT version from a source-backed item payload, validating unique item codes, decimal prices, currency/tax/discount/scope and content hash; do not activate.

### Frozen command/result contract

`ServicePriceBookItemInput` is a frozen, keyword-only DTO with exact fields `item_code: str`
and `unit_price: Decimal`. `ImportServicePriceBookCommand` is a frozen, keyword-only DTO with
exact fields `source_classification: str`, `book_version: str`, `scope_key: str`,
`currency: str`, `tax_policy: str`, `discount_policy: str`, `source_reference: str`,
`source_content: str`, `expected_source_content_hash: str`,
`items: tuple[ServicePriceBookItemInput, ...]`, `effective_from: datetime`,
`effective_to: datetime | None`, `actor_id: str`, `idempotency_key: str`, and
`runtime_profile: str`.

`ImportServicePriceBookResult` exposes exact persisted fields `price_book_id`,
`source_classification`, `book_version`, `scope_key`, `currency`, `tax_policy`,
`discount_policy`, `source_reference`, `source_content_hash`, `item_snapshot_hash`,
`item_count`, `status`, `effective_from`, `effective_to`, `created_by`, and
`disposition: CREATED|REUSED`.

- Required text is already-trimmed, nonempty, contains no NUL, and fits its carrier column;
  `scope_key` is exactly `GLOBAL`, `currency` is exactly three uppercase ASCII letters, and
  classification is exactly `PRODUCTION|TEST_ONLY`. `TEST_ONLY` import additionally requires
  `runtime_profile='test'`; it is never inferred from a name or source reference.
- The effective timestamps are naive `datetime` values and `effective_to`, when present, is
  strictly later than `effective_from`.
- At least one item is required. Item codes are already-trimmed, nonempty, NUL-free, at most
  128 characters and unique by exact code. Each price must be an actual finite `Decimal`,
  strictly positive, and have at most two fractional decimal places; no float, integer, string,
  rounding or numeric coercion is accepted.
- The canonical source snapshot is compact sorted-key UTF-8 JSON over exact keys
  `source_content` and `source_reference`. Its lowercase SHA-256 must exactly equal the supplied
  64-character lowercase hexadecimal hash. The stored item snapshot is compact sorted-key UTF-8
  JSON over exact header keys `currency`, `discount_policy`, `items`, `scope_key`, and
  `tax_policy`; items are sorted by exact item code and prices are canonical fixed-point strings.
  Its SHA-256 is stored separately. JSON framing, rather than delimiter concatenation, binds all
  values unambiguously.
- Shape/type/format failures are `SERVICE_PRICE_BOOK_IMPORT_INVALID` with status 400. Source
  hash mismatch, idempotency mismatch, duplicate version, stored replay-integrity failure and
  database write collision are `SERVICE_PRICE_BOOK_IMPORT_CONFLICT` with status 409.
- Exact idempotency replay reuses only the same untouched DRAFT tuple. The service may `flush`
  but never commits or rolls back; transaction completion remains caller-owned.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-SERVICE-RATE-VERSION:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell (verbatim): carrier

### Shared ownership serialization

- `backend/app/modules/fees/service_price_book.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01.md`
- `backend/app/modules/fees/service_price_book.py`
- `backend/tests/test_v8_service_price_book_import.py`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Import itself does not read, confirm or activate `DG-SERVICE-RATE-VERSION:GLOBAL`. The missing
  real production input does not block this development/import capability; production activation
  and production use remain separately gated and outside this task.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_service_price_book_import.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_service_price_book_import.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/service_price_book.py tests/test_v8_service_price_book_import.py && .venv/bin/ruff format app/modules/fees/service_price_book.py tests/test_v8_service_price_book_import.py && .venv/bin/ruff check app/modules/fees/service_price_book.py tests/test_v8_service_price_book_import.py`
- `git diff --check -- backend/app/modules/fees/service_price_book.py backend/tests/test_v8_service_price_book_import.py tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01.md`

## Git-Native Evidence

- Exact RED: focused test exited 1 because the import module was absent.
- Exact GREEN: focused test passed `16 passed`.
- Commit SHA and independent PROTECTED review are recorded by the integration owner after the
  scoped checks below remain current.

## Done Definition

The exact RED is observed; the minimum allowlisted change makes the exact GREEN pass; task-scoped
lint/format/diff checks pass; SQLite verification is serialized; `backend/uv.lock` remains outside
the commit; and an independent High reviewer approves the exact commit with zero P0/P1/P2
findings. Only the independent integration owner may then report this PROTECTED story PASS.

## Latest-Wins Input Activation Dependency Interpretation

Development prerequisite: adopted successor + exact code dependencies.
Production prerequisite: original DG-* gate plus reviewed active real input.
Missing production input: 409 / NO WRITE; does not block RED/GREEN or CAPABILITY_READY.
Existing closure, non-closure, allowlist, permissions and primary test remain intact.
