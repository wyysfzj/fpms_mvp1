# Contract — V8 Grant Instruction Obligation Adapter

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
  (ordinal `119`).
- Outcome: add one typed, service-only adapter that links an explicitly named grant-fee
  task and confirmed grant-notice activity to their exact accepted grant-year annuity
  obligation, then delegates one explicit client instruction to the accepted generic writer.
- Boundary decision: this story does **not** rewire the legacy PUT/batch endpoints. Their
  payloads lack actor and idempotency authority and require a separately contracted API
  successor if they are later migrated.

## Exact public contract

`backend/app/modules/grant_fees/service.py` adds:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class RecordGrantFeeTaskInstructionCommand:
    grant_fee_task_id: str
    source_activity_id: str
    instruction: str
    actor_id: str
    idempotency_key: str

@dataclass(frozen=True, slots=True)
class RecordGrantFeeTaskInstructionResult:
    grant_fee_task_id: str
    fee_obligation_id: str
    instruction: FeeClientInstruction
    activity_id: str
    idempotency_key: str
    reused: bool

def record_grant_fee_task_instruction(
    command: RecordGrantFeeTaskInstructionCommand,
    transaction: Session,
) -> RecordGrantFeeTaskInstructionResult:
    ...
```

The command must be the exact type. Every string is nonempty, already stripped and
NUL-free; task/activity/actor IDs have maximum length 36 and the idempotency key maximum
length 128. Instruction is exactly `PAY`, `HOLD` or `ABANDON`, without normalization or
legacy aliases. Invalid input is `GRANT_INSTRUCTION_COMMAND_INVALID` (400) with
`details.field`; missing task is `GRANT_INSTRUCTION_TASK_NOT_FOUND` (404); a missing
required task/activity/obligation/recognition link is `GRANT_INSTRUCTION_LINK_NOT_FOUND`
(404); contradictory or ambiguous lineage is `GRANT_INSTRUCTION_LINEAGE_CONFLICT` (409).
After delegation, preserve the generic writer's codes and details unchanged.

## Exact resolution and validation

Reject a transaction that already has pending new, dirty or deleted state. Load only the
named grant-fee task and named lifecycle activity; never select latest-by-case/document.
Require task type `GRANT` and the exact accepted Row130 confirmed
`GRANT_REGISTRATION_NOTICE_RECORDED` activity for the same case, task and source document.
Revalidate its canonical snapshot/hash, reviewed evidence identity/hash, evidence links,
due date, deadline provenance and direct correction lineage using the accepted Row130
validators.

Resolve exactly one `(case_id, source_activity_id,
obligation_type="GRANT_YEAR_ANNUITY")` obligation. Revalidate its complete accepted Row130
projection: `GOV`, `CNY`, verified source, exact document/activity/due date, category fee
code, complete annual line set and fields, current or historical correction identity, and
exactly one same-case `FEE_OBLIGATION_RECOGNIZED` activity naming it. Zero, multiple,
partial, stale, divergent or ambiguous facts fail before delegation.

Delegate exactly once to `record_client_instruction` with the resolved obligation,
`FeeClientInstruction(command.instruction)`, and the unchanged actor/idempotency key.
Return only the task/obligation identity plus the delegated instruction, activity ID, key
and `reused` result.

## Replay, transaction and non-goals

Idempotency remains the deep writer's `(case_id, key)` scope. Exact replay returns the
original result with `reused=True`; same-key drift and new-key same-state requests remain
the accepted 409 conflicts. Exact historical replay through one intact direct grant-notice
correction remains supported.

The adapter performs no commit, rollback, refresh, clock/UUID generation or retry. Failure
before delegation is write-free; the generic writer owns its savepoint/race recovery, and
caller rollback removes header, instruction activity and lifecycle revision together.
Never mutate the legacy task instruction/counters/draft flags, deadline or evidence facts,
case lifecycle/legal status, draft, PayList, payment, document or evidence. No API/schema,
migration, rate/reduction rule or automatic draft is included.

## Allowed product scope and verification

- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_v8_grant_instruction_obligation_adapter.py`

The focused RED/GREEN must cover the exact DTO/callable, all three instructions, validation,
explicit named selection, zero/multiple links, full Row130 lineage/projection validation,
original/corrected selection, historical and exact replay, collisions, caller rollback,
forced deep failure, delegate-once and every non-goal. Serialize SQLite verification.

Affected regressions:

- `backend/tests/test_v8_grant_instruction_obligation_adapter.py`
- `backend/tests/test_v8_grant_year_annuity_obligation.py`
- `backend/tests/test_v8_fee_obligation_instruction.py`
- `backend/tests/test_v8_grant_notice_lifecycle_adapter.py`

Final checks are scoped Ruff/format/diff and an independent High review of the exact commit.
