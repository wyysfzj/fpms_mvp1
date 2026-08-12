# FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `228`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `736`
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

Create service-domain obligation from an approved service item without deriving it from official fee.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01`
- `FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01`

### External, gate and inherited prerequisites

- `gate` — `DG-SERVICE-RATE-VERSION:GLOBAL`: Persisted, current, source-backed decision must be confirmed for this exact scope.

- Approved source dependency cell (verbatim): activation

### Shared ownership serialization

- `backend/app/modules/fees/obligation_service.py` order key `8`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01.md`
- `backend/app/modules/fees/obligation_service.py`
- `backend/tests/test_v8_service_receivable_obligation.py`
- `artifacts/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Require the exact persisted gate and lane activation; absent/revoked/future/scope-mismatched decisions are 409/no write.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_service_receivable_obligation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_service_receivable_obligation.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_service_receivable_obligation.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_service_receivable_obligation.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_service_receivable_obligation.py`
- `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_service_receivable_obligation.py tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01` pass. Only then may this task be reported PASS.

## Latest-Wins Input Activation Dependency Interpretation

Development prerequisite: adopted successor + exact code dependencies.
Production prerequisite: original DG-* gate plus reviewed active real input.
Missing production input: 409 / NO WRITE; does not block RED/GREEN or CAPABILITY_READY.
Existing closure, non-closure, allowlist, permissions, primary tests and evidence remain intact.

## Frozen Service Receivable Contract (2026-08-13)

- Entry point `create_service_receivable_obligation(command, transaction)` accepts exact
  `price_book_version_id`, `item_code`, `case_id`, server actor/time and idempotency key. It never
  commits or rolls back.
- Resolve exactly the named sole current `GLOBAL` `PRODUCTION/ACTIVE` service-price book effective
  at server time, validate its complete canonical stored snapshot, and resolve the current effective
  `DG-SERVICE-RATE-VERSION:GLOBAL` tuple exactly as activation does. Missing/inactive/non-current,
  malformed, interval, gate/source/hash or item mismatch is `SERVICE_RECEIVABLE_CONFLICT / 409`
  before any write.
- Select exactly one canonical item. Append/reuse a confirmed FEE source activity whose payload and
  evidence bind price-book ID/version/source hash/item-snapshot hash, exact item code/unit price,
  currency/tax/discount and recognition time. Then call the frozen generic recognition seam with
  `fee_domain=SERVICE`, `obligation_type=SERVICE_FEE`, no source document, no official amount, zero
  reduction, payable/source amount equal to the approved service unit price and official evidence
  `NOT_APPLICABLE` through existing domain behavior.
- The source activity and result durably preserve the exact approved item code up to the
  price-book carrier's 128-character limit. Because the inherited obligation-line `fee_code`
  carrier is limited to 64 characters and schema change is outside this closure, codes of at most
  64 characters are stored unchanged; longer codes use the complete lowercase SHA-256 hex digest
  of the exact UTF-8 item code as the deterministic line identity. The exact item code is never
  truncated and remains recoverable from the source activity linked by `source_activity_id`.
- The external idempotency key has one global durable owner across all cases. Both derived source
  and recognition activity keys must be absent together or form one complete same-case linked
  tuple; cross-case ownership, multiplicity, partial tuples or mismatched activity types/lineage
  return `SERVICE_RECEIVABLE_CONFLICT / 409` before any write.
- Exact replay reuses both source activity and obligation; a differing book/item/case/actor or stored
  source tuple conflicts. No official rate, CNIPA amount, GovPayment, PayList, draft, client
  instruction, payment or official-evidence fact is created or inferred.
