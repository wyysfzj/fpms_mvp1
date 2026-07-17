# FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01

Status: READY FOR HIGH / CHANGED-MECHANISM RECOVERY / VALID RED PRESERVED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `110`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `538`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Read one obligation with source, item lines and seven separated states; no status/amount inference or write.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Execution Blocker (2026-07-14)

High execution stopped before RED or product edits because the approved sources do not
uniquely freeze the read-service contract. `FeeObligation` and its field order/types are
frozen, but the following observable behavior is not:

- public callable name, parameter order and keyword-only boundary;
- exact 404/409 codes for missing, corrupt or multiplicity-conflicting persisted facts;
- the persisted source for `pay_list_status` instead of an inferred/default value;
- recognition/source/line consistency and current/superseded-line validation;
- dirty-session/no-autoflush behavior and the exact bounded SELECT count.

At least `get_fee_obligation(transaction, *, obligation_id)` and
`read_obligation_detail(obligation_id, transaction)` are credible repository-style seams.
Reusing the existing recognition-result helper is also not equivalent to a read contract
because that helper requires recognition activity/idempotency result metadata and currently
defaults `pay_list_status`. Ultra must freeze and materialize the exact contract before this
task returns to High implementation.

## Ultra Contract Freeze — 2026-07-14

This section is authoritative for High implementation. It materializes section 7 of
`docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
without changing this task's one read-service closure slice. The accepted F3 carrier is
an added prerequisite; product implementation remains NOT STARTED.

### Frozen public seam and request validation

```python
def get_fee_obligation(
    obligation_id: str,
    transaction: Session,
) -> FeeObligation:
```

- Reuse the frozen `FeeObligation` and its nested DTOs exactly. Do not add a duplicate
  read DTO, wrapper result, overload, keyword-only boundary or alternate public name.
- `obligation_id` must be a `str`, nonblank, already stripped, contain no NUL and have
  length at most 36. Do not trim, normalize or substitute it. Any violation is 400
  `FEE_OBLIGATION_DETAIL_INVALID` with exact details
  `{"field": "obligation_id"}` and executes zero SQL.
- A valid ID whose header does not exist is 404 `FEE_OBLIGATION_NOT_FOUND` after exactly
  one header SELECT.
- Once the header exists, any missing relation, cross-link, malformed stored value or
  illegal multiplicity is 409 `FEE_OBLIGATION_STORED_STATE_INVALID`; persisted corruption
  must not be reported as a request 404.

### Frozen DTO projection and persisted-state validation

- Set `estimate_status=None`. Project the stored obligation, client-instruction, draft,
  payment and official-evidence status through their exact frozen enums. An invalid stored
  enum is stored-state 409. No status dimension may default, promote, demote or infer any
  other dimension.
- Set `pay_list_status=CREATED` if and only if at least one legal persisted relation exists
  through `ObligationLine -> FeeObligationDraftItemLink -> FeeItem -> GovPayment ->
  PayList`; otherwise set it to `NOT_CREATED`. PayList or GovPayment status must never
  infer payment or official-evidence status, and no future PayList activity adapter is a
  dependency.
- A `SERVICE` obligation with any GOV PayList relation is stored-state 409. Any traversed
  obligation/line/draft-item/payment/PayList relation whose case or currency conflicts with
  the header is also stored-state 409.
- Require at least one line and exact uniqueness of `(fee_code, fee_year_key)`. Return lines
  sorted by `(fee_code, fee_year_key, id)`. Preserve stored `Decimal` and `date` values;
  do not stringify, round or recalculate them.
- Header, lines, source activity, the unique recognition activity and canonical payload,
  current identity and supersede linkage must satisfy the accepted recognize contract.
  Missing, cross-linked, malformed or multiply matched facts are stored-state 409.
- A valid historical obligation with `obligation_status=SUPERSEDED` is readable. Do not
  restrict lookup to current obligations or infer any later state into its returned detail.

### Frozen transaction and query boundary

- Enclose all persisted reads in `transaction.no_autoflush` and use explicit selected
  columns plus mapping rows. Ignore and preserve the caller's unflushed `new`, `dirty` and
  `deleted` state, and do not populate, replace, refresh, expire or otherwise pollute the
  session identity map.
- Invalid input executes zero SELECTs; a missing header executes exactly one SELECT; a
  successful detail executes exactly four SELECTs in this order: header, lines,
  source-plus-recognition activities, and the PayList relation set. No N+1 query is legal.
- The service performs no INSERT, UPDATE or DELETE and does not call `add`, `flush`,
  `commit`, `rollback`, `begin_nested`, `refresh` or `expire`. It takes no lock, reads no
  clock and mutates no ORM object or caller-owned pending identity state.

### Frozen RED / GREEN matrix

`backend/tests/test_v8_fee_obligation_detail_read.py` must use a real
foreign-key-enabled SQLite session and prove all cases through `get_fee_obligation()`:

1. RED: the exact synchronous public callable/signature and frozen DTO-returning behavior
   are absent; an alternate helper, endpoint or duplicate read DTO does not satisfy RED.
2. Validation: wrong type, blank, leading/trailing whitespace, NUL and length greater than
   36 each return the exact 400 code/details and execute zero SQL; a stripped nonblank
   length-36 ID reaches the header lookup unchanged.
3. Missing and corruption boundary: an absent header returns exact 404 after one SELECT;
   every post-header missing/cross-link/malformed/multiplicity fixture returns exact 409,
   never 404.
4. Base GREEN: a valid GOV obligation returns the exact frozen header/source/line DTOs,
   `estimate_status=None`, exact independent enum projections, unchanged Decimal/date
   values and lines sorted by `(fee_code, fee_year_key, id)`.
5. PayList relation matrix: no persisted complete chain returns `NOT_CREATED`; one or more
   legal complete F3-to-PayList chains return `CREATED`; orphaned or cross-linked partial
   chains fail stored-state 409 and never use PayList/GovPayment status for another status.
6. Domain consistency: a SERVICE-to-GOV-PayList relation and each case/currency mismatch
   at a traversed relation independently return stored-state 409.
7. Line integrity: zero lines, a duplicate `(fee_code, fee_year_key)`, a cross-obligation
   line and malformed stored line values each return stored-state 409; intentionally
   unsorted legal lines return in the exact frozen order.
8. Recognition integrity: missing/duplicate/cross-case source or recognition activity,
   malformed canonical payload, current-identity mismatch and broken supersede linkage
   each return stored-state 409 under the accepted recognize contract.
9. Historical read: a valid `SUPERSEDED` obligation succeeds by exact ID with its own
   source, lines and stored seven-state projection; it is not replaced by or inferred from
   the current obligation.
10. Read-only/query proof: spies assert 0/1/exact-4 SELECT budgets, the exact query order,
    no N+1, `no_autoflush`, explicit mappings, no mutation/transaction/lock/clock calls,
    and byte-for-byte preservation of pre-existing unflushed new/dirty/deleted and identity
    state before and after success and error paths.

GREEN requires the complete matrix plus the listed inherited regressions; it does not
authorize endpoint, UI, schema, write, activity append or PayList-adapter behavior.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
- `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): client instruction; serialized
- Approved delta-2 dependency: accepted `FPMS-V8-W1-F3-OBLIGATION-DRAFT-LINK-CARRIER-20260712-01`; no future PayList activity adapter.

### Shared ownership serialization

- `backend/app/modules/fees/obligation_service.py` order key `4`; project this order only across owners present in the active manifest.
- SQLite verification for this task is globally serialized even though the service itself is read-only.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01.md`
- `backend/app/modules/fees/obligation_service.py`
- `backend/tests/test_v8_fee_obligation_detail_read.py`
- `artifacts/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All task-owned and inherited SQLite verification and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_detail_read.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_detail_read.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_contracts.py tests/test_v8_fee_obligation_recognize.py tests/test_v8_fee_obligation_instruction.py tests/test_v8_w1_f3_obligation_draft_link.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_detail_read.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_detail_read.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_detail_read.py`
- `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_fee_obligation_detail_read.py tasks/postdemo/v8/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins recovery authority

- Authoritative recovery contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, Task 110 lines 780–795.
- Supplemental authority: row `23 / M4-F / H4-R` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; `chosen_runbook: P0-prereq-heavy-story` remains authoritative.
- Classification is exact **NO CONTRACT CHANGE** and creates no new product node. The existing closure, non-closure, dependencies, Allowed Files and all other inherited bytes remain binding.

### Preserved durable recovery state

- Preserve the valid RED at `artifacts/FPMS-V8-FO-OBLIGATION-DETAIL-READ-20260712-01/outputs/20260715T105402_red.log` as the task's RED evidence.
- Preserve the existing 728-line partial `backend/tests/test_v8_fee_obligation_detail_read.py` and the current Evidence 1.1 baseline and artifacts byte-for-byte until High resumes.
- Do not reinitialize evidence, rerun RED or spawn another identical controller worker. Resume from the first incomplete GREEN increment without recapturing or absorbing the dirty baseline.

### Changed-mechanism High recovery

- Resume only in a changed-mechanism High lane owned by the otherwise-unassigned main thread or one bounded direct worker owning this exact task.
- Complete the missing historical, source-lineage, current/supersede and read-only coverage in small durable increments; after each increment inspect allowlist diff and artifact growth.
- Apply the repository two-observation no-progress and liveness-recovery rules exactly. Do not interrupt active preflight or serialized verification, and do not launch repeated replacement workers.

### Unchanged product contract and gates

- Preserve the frozen `get_fee_obligation(obligation_id, transaction) -> FeeObligation` seam, existing DTOs, exact request `400`, missing-header `404`, stored-state `409`, zero/one/exact-four SELECT budgets, `no_autoflush`, explicit mappings and identity-map preservation.
- Preserve the exact four successful SELECTs in order: header, lines, source-plus-recognition activities, then PayList relations. No N+1, inference, defaulting, mutation, write, lock, clock or caller-transaction action is authorized.
- Existing targeted GREEN/regressions, scoped Ruff/format/diff, serialized SQLite verification, Evidence 1.1 continuation/finalization, independent review, repository task gate, atomic evidence validation and Done Definition remain unchanged for High.
- This Ultra recovery classification performs no product/test/evidence edit and runs only the atomic task-file check.
