# FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `107`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md` §3
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `535`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Record or exactly replay one `PAY/HOLD/ABANDON` instruction against one eligible recognized
fee obligation, update only its client-instruction header fact, and append/reuse exactly one
unchanged-centre `FEE_CLIENT_INSTRUCTION_RECORDED` activity in the same caller-owned
transaction. A changed instruction supersedes the previous instruction activity; no draft or
case legal-status change is implied.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-13

This section is the complete High implementation contract. It freezes the service boundary,
state gate, audit activity, idempotency, concurrency and no-side-effect behavior without
adding an HTTP route, a customer policy gate or a mandatory attachment.

### Exact public callable and frozen values

`backend/app/modules/fees/obligation_service.py` exposes exactly this public callable;
helpers remain private:

```python
def record_client_instruction(
    command: RecordFeeObligationInstructionCommand,
    transaction: Session,
) -> RecordFeeObligationInstructionResult:
    ...
```

- Parameter order, names and annotations are exact. Import the command, result,
  `FeeClientInstruction`, `FeeClientInstructionStatus` and all nested result values from the
  frozen `obligation_contracts.py`; do not accept a dictionary, Pydantic schema or a second
  command/result shape.
- `transaction` is an existing SQLAlchemy `Session`. The service may open one nested
  savepoint and call `flush()`, but must not call outer `commit()`, outer `rollback()` or
  close the session.
- The session must have no pending `new`, `dirty` or `deleted` objects on entry. Violation
  reuses `FEE_OBLIGATION_TRANSACTION_DIRTY` (409) before any service write.
- No public exception, repository, clock parameter, permission dependency or HTTP adapter is
  authorized. Business failures use existing `app.core.errors.BusinessError`.

### Exact command validation and lookup order

Validation is strict and non-coercing. Preserve strings exactly after validation and use
enum `.value` only for persistence/payload output.

1. Require exactly `RecordFeeObligationInstructionCommand`; `instruction` must be a real
   `FeeClientInstruction`; and require non-blank `obligation_id`/`actor_id` of at most 36
   characters and `idempotency_key` of at most 128 characters. Failure is
   `FEE_CLIENT_INSTRUCTION_COMMAND_INVALID` (400), message `客户费用指示命令无效`, with
   `details={"field": "<exact field>"}`.
2. Missing `FeeObligation(command.obligation_id)` is `FEE_OBLIGATION_NOT_FOUND` (404),
   message `费用义务不存在`.
3. Load its `Case`; an impossible missing parent reuses `CASE_NOT_FOUND` (404). Before state
   gating, look up `(case_id, idempotency_key)` and apply the replay contract below. Thus an
   exact prior fact remains replayable after a later instruction, draft, payment, official
   proof or supersede; malformed input never replays.
4. Resolve exactly one same-case `FEE` activity of type `FEE_OBLIGATION_RECOGNIZED` whose
   `FPMS_FEE_OBLIGATION_RECOGNIZED_V1` payload names this obligation. Missing, duplicate,
   malformed or cross-linked recognition is
   `FEE_CLIENT_INSTRUCTION_RECOGNITION_INVALID` (409), message
   `费用义务识别活动无效`.
5. Validate the persisted header and prior-instruction linkage, then apply the eligibility
   gate and same-target rule below. An unknown stored enum, a `PENDING` header with an
   instruction activity, a non-`PENDING` header without one current activity, a malformed
   V1 payload, or a current activity whose instruction differs from the header is
   `FEE_CLIENT_INSTRUCTION_STORED_STATE_INVALID` (409), message
   `客户费用指示存量状态无效`.

### Eligibility and instruction transitions

A new activity is allowed only while all four header predicates hold:

```text
obligation_status == RECOGNIZED
draft_status == NOT_CREATED
payment_status == UNPAID
official_evidence_status != VERIFIED
```

- These predicates make a superseded obligation, created draft, paid obligation or verified
  official proof immutable. Failure is `FEE_CLIENT_INSTRUCTION_LOCKED` (409), message
  `当前费用义务已锁定，不能修改客户指示`, with details containing exactly
  `obligation_id`, `obligation_status`, `draft_status`, `payment_status` and
  `official_evidence_status` as stored.
- The current instruction may be `PENDING`, `PAY`, `HOLD` or `ABANDON`. The frozen command
  can target only `PAY`, `HOLD` or `ABANDON`; `PENDING` is the initial fact, not a write
  action. Before downstream execution, any current state may change to a *different* command
  target.
- A new idempotency key targeting the already-current instruction is not a replay and must
  raise `FEE_CLIENT_INSTRUCTION_SAME_STATE` (409), message
  `客户费用指示已处于目标状态`, with no write.
- `ABANDON` applies only to this fee obligation. It must not modify or imply any
  `Case.business_stage`, `official_procedure_stage`, `legal_status`,
  `lifecycle_verification_status` or legacy `Case.status` value and must not be interpreted
  as abandonment of the application/patent right.

### Exact activity and payload

For a new fact, capture one timezone-naive UTC timestamp and construct exactly one
`LifecycleEventCommand`:

- `case_id=<obligation case>`;
- `event_type="FEE_CLIENT_INSTRUCTION_RECORDED"`, `lane=ActivityLane.FEE`;
- `effective_at=occurred_at=<the one captured timestamp>`;
- `actor_id=command.actor_id`, `reviewer_id=None`;
- `idempotency_key=command.idempotency_key`;
- `source_activity_id=<the unique recognition activity id>`;
- `supersedes_event_id=None` when the current header is `PENDING`, otherwise the exact
  current instruction activity id;
- `confirmation_status=ConfirmationStatus.CONFIRMED`;
- `evidence_refs=()` and the exact payload below.

```json
{
  "actor_id": "<command actor_id>",
  "instruction": "PAY | HOLD | ABANDON",
  "obligation_id": "<command obligation_id>",
  "previous_instruction_status": "PENDING | PAY | HOLD | ABANDON",
  "schema": "FPMS_FEE_CLIENT_INSTRUCTION_RECORDED_V1"
}
```

Serialize through the frozen lifecycle append seam; no extra label, attachment ID, legal
status, draft/payment implication or hidden metadata is allowed. Pass the current case
projection as both previous/current projection, unchanged `Case.status` as
`legacy_case_status`, and `conflict_codes=()`. The activity therefore has
`center_changes={}` and increments only the shared lifecycle revision.

Every instruction activity for the obligation keeps the same recognition
`source_activity_id`. A changed instruction points `supersedes_event_id` to the immediately
previous instruction activity; it does not supersede the recognition activity or mutate an
older activity. The latest valid instruction activity must agree with the header.

There is no mandatory attachment or evidence-reference input. The authenticated actor and
the append-only activity are the audit fact for this closure; a future requirement to retain
the customer's original email/document is a separate task.

### Idempotency, result and atomic write

- **Same key, same facts:** the existing activity must have the exact type/lane, actor,
  recognition source, supersede linkage, empty evidence set and canonical V1 payload for
  the command. Reconstruct the stored lifecycle command and use `append_case_activity()` to
  verify exact replay. Return its activity id and the current persisted frozen obligation
  snapshot with `idempotency_key=command.idempotency_key`, `reused=True`; write and flush
  nothing. Later instruction/downstream state is not rewound.
- **Same key, different facts:** any command, payload, source, actor, linkage, confirmation
  or evidence mismatch is `FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT` (409), message
  `幂等键已用于不同的客户费用指示事实`, with no write.
- **New key, same target:** use the exact same-state 409 above; an existing state is never
  silently aliased to a new key.
- **New key, changed target:** inside one `transaction.begin_nested()` savepoint, append the
  activity/revision and update the header with one compare-and-swap whose predicate includes
  the previously read instruction plus all four eligibility states. Set only
  `client_instruction_status`, `updated_by` and the existing update timestamp. A later CAS
  miss rolls back the activity and revision with the savepoint.
- Return `RecordFeeObligationInstructionResult` with the updated frozen `FeeObligation`, the
  appended activity id, the command idempotency key and `reused=False`. All seven status
  dimensions other than `client_instruction_status`, every obligation/line/source fact,
  all case projections and `Case.status` remain unchanged.

The service only flushes; visibility and durability belong to the caller's commit. Caller
rollback must remove the header change, activity and lifecycle revision together.

### Exact race handling

- Treat only the activity `(case_id, idempotency_key)` uniqueness failure and the header CAS
  miss as recognized races. Let the nested savepoint roll back before one reread; never roll
  back the outer transaction.
- After an activity-key race, exact same-key/same-fact state returns `reused=True`; a visible
  mismatch uses the exact idempotency 409. If the competing activity is not visible, raise
  `FEE_CLIENT_INSTRUCTION_CONCURRENCY_CONFLICT` (409), message
  `并发客户费用指示尚不可见，请重试完整事务`.
- After a header CAS miss, reread once. A now-visible draft/payment/official-proof/supersede
  uses the exact locked 409; a now-visible same target under another key uses the exact
  same-state 409; any other instruction change uses
  `FEE_CLIENT_INSTRUCTION_CONCURRENCY_CONFLICT`. Do not silently reorder two concurrent
  different instructions.
- Foreign-key, check, type or unclassified integrity failures are re-raised. SQLite
  `database is locked`/driver errors are neither converted nor retried by this service.

### Frozen RED / GREEN / replay / race / no-side-effect matrix

`backend/tests/test_v8_fee_obligation_instruction.py` must use real foreign-key-enabled
SQLite sessions and prove all of the following through `record_client_instruction()`:

1. RED: the exact public callable/behavior is initially missing; no substitute endpoint or
   direct model edit satisfies the test.
2. GREEN: each target `PAY/HOLD/ABANDON` succeeds from `PENDING`; a later different target
   succeeds before downstream work, changes only the header instruction/audit update fields,
   appends one `CONFIRMED` FEE activity with the exact V1 payload/source/supersede linkage,
   keeps `center_changes={}`, `Case.status` and all four central carriers unchanged, and
   returns the exact frozen result with `reused=False`.
3. Replay: same key/same facts returns the original activity with `reused=True` and no row,
   header or revision change, including after a later instruction or downstream lock; same
   key with changed obligation/instruction/actor/activity facts is the exact idempotency 409.
4. Same-state: a new key targeting the current instruction is the exact same-state 409 and
   creates no activity or revision.
5. Lock matrix: independently set obligation `SUPERSEDED`, draft `CREATED`, payment `PAID`
   and official evidence `VERIFIED`; each receives the exact locked 409 and no mutation.
6. Stored/link validation: missing obligation/case, missing/duplicate/malformed recognition,
   invalid command fields and inconsistent prior-instruction/header facts raise the exact
   frozen status/code in the stated order with no mutation.
7. Race matrix: simulate same-key/same-fact replay recovery, same-key/different-fact conflict,
   new-key same-target conflict, different-target header-CAS loss, downstream-lock CAS loss
   and not-yet-visible activity conflict while the outer session remains usable.
8. Atomicity/no side effects: caller rollback and a forced failure after activity append both
   remove the header change, activity and revision; no service commit/outer rollback occurs;
   no draft, PayList, payment/evidence link, attachment/document, case projection or legacy
   status is read as an instruction trigger or written by this service.

The serialized inherited regression command is:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_fee_obligation_contracts.py \
  tests/test_v8_fee_obligation_recognize.py \
  tests/test_v8_lifecycle_activity_append.py
```

### Reaffirmed non-closure

No endpoint, permission/API status mapping, UI, schema/migration, instruction attachment,
customer-policy engine, draft creation, PayList, payment, official-proof verification,
obligation supersede, case lifecycle/legal-status transition, legacy annuity/grant adapter,
commit or retry loop. This service records one instruction fact only.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
- `FPMS-V8-LC-ACTIVITY-APPEND-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): recognize

### Shared ownership serialization

- `backend/app/modules/fees/obligation_service.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01.md`
- `backend/app/modules/fees/obligation_service.py`
- `backend/tests/test_v8_fee_obligation_instruction.py`
- `artifacts/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_instruction.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_instruction.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_instruction.py && .venv/bin/ruff format app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_instruction.py && .venv/bin/ruff check app/modules/fees/obligation_service.py tests/test_v8_fee_obligation_instruction.py`
- `git diff --check -- backend/app/modules/fees/obligation_service.py backend/tests/test_v8_fee_obligation_instruction.py tasks/postdemo/v8/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01` pass. Only then may this task be reported PASS.
