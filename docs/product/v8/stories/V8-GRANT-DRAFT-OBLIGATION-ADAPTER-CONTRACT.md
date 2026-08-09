# Contract — V8 Grant Draft Obligation Adapter

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01`
  (ordinal `120`).
- Outcome: add one typed, service-only adapter that resolves an explicitly named grant-fee
  task and confirmed grant-notice activity to their exact accepted grant-year annuity
  obligation, then delegates draft preparation once to the accepted generic writer.
- Boundary decision: this story does **not** rewire the legacy bodyless draft POST. It
  carries no source activity or idempotency key and requires a separately contracted API
  successor if later migrated.

## Exact public contract

`backend/app/modules/grant_fees/service.py` adds:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class PrepareGrantFeeTaskDraftCommand:
    grant_fee_task_id: str
    source_activity_id: str
    actor_id: str
    idempotency_key: str

@dataclass(frozen=True, slots=True)
class PrepareGrantFeeTaskDraftResult:
    grant_fee_task_id: str
    fee_obligation_id: str
    draft_id: str
    links: tuple[FeeDraftItemLinkResult, ...]
    activity_id: str
    activity_reused: bool
    idempotency_key: str

def prepare_grant_fee_task_draft(
    command: PrepareGrantFeeTaskDraftCommand,
    transaction: Session,
) -> PrepareGrantFeeTaskDraftResult:
    ...
```

The command must be the exact type. Every string is nonempty, already stripped and
NUL-free; task/activity/actor IDs have maximum length 36 and the idempotency key maximum
length 128. Invalid input is `GRANT_DRAFT_COMMAND_INVALID` (400) with `details.field`;
missing task is `GRANT_DRAFT_TASK_NOT_FOUND` (404); a missing required activity,
obligation or recognition is `GRANT_DRAFT_LINK_NOT_FOUND` (404); contradictory,
ambiguous, stale, malformed or returned-result lineage is
`GRANT_DRAFT_LINEAGE_CONFLICT` (409). After delegation, preserve the accepted generic
writer's codes/details unchanged.

## Exact resolution and delegation

Reject a transaction that already has pending new, dirty or deleted state. Load only the
named task and named grant-notice activity. Reuse the accepted Row119 resolution and full
Row130 validation: confirmed same-case `GRANT_REGISTRATION_NOTICE_RECORDED`; exact task,
source document, reviewed evidence, canonical snapshot/hash, deadline and direct correction
lineage; exactly one `(case_id, source_activity_id,
obligation_type="GRANT_YEAR_ANNUITY")` obligation and one recognition activity; and the
complete `GOV`/`CNY`/`VERIFIED` header and annual-line projection.

Delegate exactly once to `prepare_draft` using the resolved obligation and unchanged actor
and idempotency key. Return the deep result's exact draft, link, activity, key and reuse
identities; never generate substitutes.

Within the generic writer's nested transaction, validate the returned draft and persisted
links: same obligation, key, case, client and currency; every returned link exists and joins
one obligation line to an item belonging to the returned draft. Any post-delegation
identity or lineage mismatch rolls back that savepoint and raises the adapter conflict.

## Replay, transaction and non-goals

Idempotency remains the deep writer's `(case_id, key)` scope. Exact replay returns the
original draft/link/activity identities with `activity_reused=True` and reused links;
same-key actor/input drift and a new key after draft creation remain 409. Historical exact
replay is permitted only through the intact explicitly named correction lineage and an
existing matching deep activity.

The adapter performs no commit, rollback, refresh, retry, clock/UUID generation or second
activity append. Caller rollback removes all delegated changes. Allowed mutation is only
the accepted Row113 draft/item/link creation or reuse, obligation draft status, and one
`FEE_DRAFT_CREATED` activity/revision. Never mutate the legacy task instruction, counters,
`draft_generated`, notice/deadline/source/amount facts, case lifecycle/legal projection,
documents/evidence, PayList, payment, rate/reduction or service receivables.

## Allowed product scope and verification

- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_v8_grant_draft_obligation_adapter.py`

The focused RED/GREEN covers the exact DTO/callable, strict validation, explicit named
selection, full Row119/130 lineage and cardinality, delegate-once, returned persisted
draft/link/activity validation, exact and historical replay, collisions, caller rollback,
forced deep/result mismatch and every non-goal. Serialize SQLite verification.

Affected regressions include the focused adapter, Row119 grant instruction adapter,
Row130 grant-year obligation, Row113 generic draft and accepted Row122 annuity draft
adapter suites. Final checks are scoped Ruff/format/diff and independent High review of the
exact commit.
