# FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `223`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `731`
- Expected manifest phase: `deferred`
- Customer gate requirement: `DG-SERVICE-RATE-VERSION[GLOBAL]`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SCHEMA`

- RED expectation: Exact schema test fails because the named table/column/index is absent.
- GREEN expectation: Exact schema test, task-scoped Ruff, unique-head check and clean temporary SQLite `upgrade head` pass.

## Exact Closure Slice

Add only versioned service price-book header with immutable validated item snapshot/source hash/approval/currency/tax/discount/scope fields; no import or activation.

## Explicit Non-Closure

No backfill, service, endpoint, seed, UI or second table/carrier. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-PAYLIST-EXPORT-ARTIFACT-CARRIER-20260712-01`
- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-SERVICE-RATE-VERSION:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell (verbatim): service-rate gate; global Alembic lock

### Shared ownership serialization

- `GLOBAL_ALEMBIC_HEAD` order key `15`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/models.py` order key `7`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01.md`
- `backend/alembic/versions/v8_w6_service_price_book.py`
- `backend/app/modules/fees/models.py`
- `backend/tests/test_v8_service_price_book_schema.py`
- `artifacts/FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Require the exact persisted gate and lane activation; absent/revoked/future/scope-mismatched decisions are 409/no write.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_service_price_book_schema.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_service_price_book_schema.py`
- `cd backend && .venv/bin/ruff check --fix alembic/versions/v8_w6_service_price_book.py app/modules/fees/models.py tests/test_v8_service_price_book_schema.py && .venv/bin/ruff format alembic/versions/v8_w6_service_price_book.py app/modules/fees/models.py tests/test_v8_service_price_book_schema.py && .venv/bin/ruff check alembic/versions/v8_w6_service_price_book.py app/modules/fees/models.py tests/test_v8_service_price_book_schema.py`
- `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head  # clean temporary SQLite database`
- `git diff --check -- backend/alembic/versions/v8_w6_service_price_book.py backend/app/modules/fees/models.py backend/tests/test_v8_service_price_book_schema.py tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01` pass. Only then may this task be reported PASS.
