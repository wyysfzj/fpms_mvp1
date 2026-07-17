# FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `136`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `578`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-RULE`

- RED expectation: Exact public rule test fails on the named transition/calculation.
- GREEN expectation: Exact rule test passes every named success/boundary/fail-closed case.

## Exact Closure Slice

Layout-design registration fee is 1000 yuan.

## High Preflight Blocker — 2026-07-15

The approved source-activation dependency freezes validation and activation of an
already-persisted CNIPA rate book, but explicitly excludes fee amounts and rate rules. It
also preserves a fail-closed development boundary with no automatically created or
activated real CNIPA rate-book version. The current public module interface exposes source
activation and estimate-provider behavior only; it does not freeze this standalone fixed
rule's callable/DTO, authoritative rate-book identity/version/effective interval, canonical
lookup key, Decimal representation, or exact fail-closed error semantics.

High implementation therefore stopped before evidence initialization, RED, or product
edits. Ultra must freeze those observable semantics in this exact task before execution;
see
`artifacts/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01/analysis/contract_ambiguity.md`.

## Explicit Non-Closure

No second event/rate/policy, persistence adapter, endpoint, seed or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): rate book

### Shared ownership serialization

- `backend/app/modules/fees/official_rate_book.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01.md`
- `backend/app/modules/fees/official_rate_book.py`
- `backend/tests/test_v8_layout_registration_fee_rule.py`
- `artifacts/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_layout_registration_fee_rule.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_layout_registration_fee_rule.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/official_rate_book.py tests/test_v8_layout_registration_fee_rule.py && .venv/bin/ruff format app/modules/fees/official_rate_book.py tests/test_v8_layout_registration_fee_rule.py && .venv/bin/ruff check app/modules/fees/official_rate_book.py tests/test_v8_layout_registration_fee_rule.py`
- `git diff --check -- backend/app/modules/fees/official_rate_book.py backend/tests/test_v8_layout_registration_fee_rule.py tasks/postdemo/v8/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LAYOUT-REGISTRATION-FEE-RULE-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority and prerequisites

- Authority: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
  lines 716–733 and supplemental batch row `27 / M4-G / H4-5`.
- Risk is `HIGH`; `chosen_runbook: P0-prereq-heavy-story` is latest-wins. The inherited
  High preflight blocker remains history, and the existing Allowed Files list is unchanged.
- D4-09 `FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01` must independently PASS
  before this rule consumes its exact inactive candidate contract.
- The accepted `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01` and
  `FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01` remain immutable prerequisites.
- Shared `official_rate_book.py` ownership is serialized exactly activation → provider →
  Task 136. Runtime success additionally requires explicit prior activation of the exact
  D4-09 candidate; this rule never activates it.

### Exact read-only layout registration fee rule

- Add only `get_layout_registration_fee(command, transaction)` with the frozen
  `GetLayoutRegistrationFeeCommand`/`GetLayoutRegistrationFeeResult` boundary.
- The command must be the exact type with a real effective date on or after `2017-07-01`;
  invalid type/date is the accepted 400 before any rate selection.
- Query fee key exactly `IC_LAYOUT_REGISTRATION_FEE`; do not normalize, alias, infer or
  substitute another item.
- Select exactly one book with `source_authority=CNIPA`, `book_code=CNIPA_LAYOUT_246`,
  `version_code=2017-07-01`, inclusive/open interval `[2017-07-01, None)`,
  `approval_status=APPROVED`, `activation_status=ACTIVE`, and an interval containing the
  requested date.
- Require its exact nonblank source reference/version, canonical `CNIPA_RATE_SOURCE_V1`
  snapshot, matching lowercase 64-hex snapshot hash and inner content hashes, plus the
  immutable activation/source facts accepted by the activation service.
- Select exactly one enabled rate linked to that exact book and source/hash tuple with
  `rate_type=GOV`, `currency=CNY`, `calc_mode=FIXED`, `allow_reduction=False`, and exact
  fee key `IC_LAYOUT_REGISTRATION_FEE`.
- The linked rate's legacy `source_status=PENDING_CONFIRMATION` remains an exact safety
  field; strict Task 136 authority is the linked book's `APPROVED/ACTIVE` state. Never
  reinterpret that field to activate an inactive candidate or borrow a generic rate.
- Stored amount must be exact two-place Decimal `1000.00`. Return it unchanged with the
  exact rate ID/key/type/currency/mode/reduction/enabled values and exact book ID/code/
  version/effective interval/approval/activation/source reference/source version/hash
  values; perform no calculation, float conversion, normalization or rounding.

### Fail-closed and no-write boundary

- Missing, inactive, unapproved, ineffective, ambiguous or multiple books; missing,
  disabled, unlinked, ambiguous or multiple rates; malformed source/version/hash/status/
  interval/amount; or any book-rate-source contradiction is the accepted 409.
- Never choose latest, database-first, adjacent, legacy-seed, customer-workbook, Tianyue,
  cached-extraction or fallback rows. Candidate existence alone is not authority to charge.
- Execute explicit reads under `transaction.no_autoflush`; use no clock and perform zero
  flush, insert, update, delete, activation, approval, retirement, commit or rollback.
- Exact repeated reads return the same persisted identities and values with no mutation;
  changed persisted source/version/hash/status/amount is revalidated and fails closed when
  it no longer full-matches this contract.

### Materialization non-closure

- This materialization changes only Status and this EOF appendix. No rate/candidate/
  activation/provider/product/test/evidence, allowlist or inherited task byte is edited.
- Only atomic `check-task` runs now; TDD, targeted verification, Evidence 1.1, independent
  review, task gates and all product execution remain deferred to High.
