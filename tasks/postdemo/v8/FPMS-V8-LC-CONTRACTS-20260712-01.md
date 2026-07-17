# FPMS-V8-LC-CONTRACTS-20260712-01

Status: PASS — ULTRA CONTRACT FROZEN 2026-07-13
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `9. Wave 2A — lifecycle foundation`
Catalog ordinal: `14`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `370`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-INTERFACE`

- RED expectation: Exact contract test fails because the named type/enum/interface is absent.
- GREEN expectation: Exact contract test and task-scoped Ruff pass.

## Exact Closure Slice

Define the three axes, lanes, confirmation states, command/result and evidence-reference interface only.

## Explicit Non-Closure

No persistence, business adapter, endpoint or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-13

This section freezes the complete public interface that High must implement in
`backend/app/modules/cases/lifecycle_contracts.py`. The module is a pure Python contract
module: it imports no SQLAlchemy, FastAPI, Pydantic, repository model or transaction type,
and it performs no persistence, event-rule lookup, state transition or evidence read.

### Exact public exports

The module exports exactly the following names, in this exact `__all__` order:

```python
__all__ = (
    "ActivityLane",
    "BusinessStage",
    "ConfirmationStatus",
    "EvidenceReference",
    "LegalStatus",
    "LifecycleEventCommand",
    "LifecycleProjection",
    "LifecycleTransitionResult",
    "OfficialProcedureStage",
)
```

No Protocol, callable implementation, exception class, ORM adapter, alias or additional
public constant is authorized. The later `apply_lifecycle_event()` module function is the
single external seam; this task freezes its value types without implementing that function
or exposing its transaction dependency here.

### Exact enum contracts

Every enum below subclasses Python 3.11 `enum.StrEnum`. Member names and string values are
identical and stable; no aliases or `_missing_` coercion are allowed.

```python
class BusinessStage(StrEnum):
    NEW_CASE = "NEW_CASE"
    FILING_PREPARATION = "FILING_PREPARATION"
    WAITING_EXTERNAL_RECEIPT = "WAITING_EXTERNAL_RECEIPT"
    PROSECUTION_MANAGEMENT = "PROSECUTION_MANAGEMENT"
    OA_REPLY_IN_PROGRESS = "OA_REPLY_IN_PROGRESS"
    GRANT_REGISTRATION_IN_PROGRESS = "GRANT_REGISTRATION_IN_PROGRESS"
    POST_GRANT_MAINTENANCE = "POST_GRANT_MAINTENANCE"
    CLOSED = "CLOSED"


class OfficialProcedureStage(StrEnum):
    NOT_SUBMITTED = "NOT_SUBMITTED"
    SUBMITTED_WAITING_RECEIPT = "SUBMITTED_WAITING_RECEIPT"
    SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE = "SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE"
    ACCEPTED = "ACCEPTED"
    PRELIMINARY_EXAMINATION = "PRELIMINARY_EXAMINATION"
    RECTIFICATION_RESPONSE = "RECTIFICATION_RESPONSE"
    PUBLISHED = "PUBLISHED"
    SUBSTANTIVE_EXAMINATION = "SUBSTANTIVE_EXAMINATION"
    OFFICE_ACTION_RESPONSE = "OFFICE_ACTION_RESPONSE"
    REEXAMINATION = "REEXAMINATION"
    GRANT_REGISTRATION = "GRANT_REGISTRATION"
    GRANT_ANNOUNCED = "GRANT_ANNOUNCED"
    PROCEDURE_CLOSED = "PROCEDURE_CLOSED"


class LegalStatus(StrEnum):
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    APPLICATION_PENDING = "APPLICATION_PENDING"
    APPLICATION_REJECTED = "APPLICATION_REJECTED"
    APPLICATION_WITHDRAWN = "APPLICATION_WITHDRAWN"
    APPLICATION_ABANDONED = "APPLICATION_ABANDONED"
    PATENT_IN_FORCE = "PATENT_IN_FORCE"
    PATENT_TERMINATED = "PATENT_TERMINATED"
    PATENT_EXPIRED = "PATENT_EXPIRED"
    PATENT_INVALIDATED = "PATENT_INVALIDATED"
    UNKNOWN = "UNKNOWN"


class ActivityLane(StrEnum):
    LIFECYCLE = "LIFECYCLE"
    DOCUMENT = "DOCUMENT"
    FEE = "FEE"


class ConfirmationStatus(StrEnum):
    NEEDS_REVIEW = "NEEDS_REVIEW"
    CONFIRMED = "CONFIRMED"
    LEGACY_UNVERIFIED = "LEGACY_UNVERIFIED"
```

`NEEDS_REVIEW` is the fail-closed state for a newly recorded fact that still requires
review. `LEGACY_UNVERIFIED` is reserved for the canonical one-time `LEGACY_IMPORT` path.
Only `CONFIRMED` permits a later lifecycle rule to change a central projection. A confirmed
`DOCUMENT` or `FEE` activity remains lane-only and still cannot change a projection.

### Exact immutable value shapes

All four classes use `@dataclass(frozen=True, slots=True, kw_only=True)`. Field order,
annotations, nullability and defaults are exact. Required fields have no default; an
explicitly nullable required field must still be supplied by keyword. There is no custom
`__post_init__`, method, property or mutable default.

```python
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleProjection:
    business_stage: BusinessStage | None
    official_procedure_stage: OfficialProcedureStage | None
    legal_status: LegalStatus | None
    lifecycle_verification_status: ConfirmationStatus | None


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceReference:
    case_id: str
    evidence_kind: str
    object_type: str
    object_id: str
    content_hash: str
    captured_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleEventCommand:
    case_id: str
    event_type: str
    lane: ActivityLane
    effective_at: datetime
    evidence_refs: tuple[EvidenceReference, ...]
    actor_id: str
    idempotency_key: str
    confirmation_status: ConfirmationStatus
    payload: Mapping[str, object]
    occurred_at: datetime | None = None
    reviewer_id: str | None = None
    source_activity_id: str | None = None
    supersedes_event_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleTransitionResult:
    case_id: str
    activity_id: str
    sequence: int
    lifecycle_revision: int
    lane: ActivityLane
    event_type: str
    confirmation_status: ConfirmationStatus
    previous_projection: LifecycleProjection
    current_projection: LifecycleProjection
    legacy_case_status: str
    idempotency_key: str
    reused: bool
    conflict_codes: tuple[str, ...] = ()
```

`LifecycleProjection` deliberately permits explicit nulls because the additive W1 carrier
must represent pre-backfill and unverified cases without inventing states. It contains the
three central axes plus their verification status; OA sequence, latest activity and legacy
precedence inputs remain owned by the later projection implementation.

`EvidenceReference` mirrors the business fields of
`t_case_activity_event_evidence`. `case_id` is explicit so the append implementation can
reject a cross-case reference before inserting a link. `evidence_kind` and `object_type`
remain open strings because document, task and fee modules introduce their own reviewed
vocabularies; this contract does not invent a closed customer-policy list. `content_hash`
is the retained source hash, not a hash computed by this contract module.

`LifecycleEventCommand` is one explicit input for lifecycle, document and fee activities.
`lane` and `confirmation_status` have no defaults so a caller cannot silently create a
central or confirmed fact. `event_type` remains a string because each later atomic rule task
owns exactly one whitelist addition. An empty evidence tuple is structurally representable;
the owning event rule decides whether evidence is mandatory. `reviewer_id`, source and
supersede references are conditional and therefore default to `None`.

`LifecycleTransitionResult` represents only a successfully appended or idempotently reused
activity. `reused=False` means this invocation appended the identified activity;
`reused=True` means the exact existing activity was returned without a write or revision
increment. `conflict_codes` is a sorted, duplicate-free tuple of non-blocking recorded
conflict/warning codes, such as legacy projection reconciliation output; its empty tuple
default means none. A blocking idempotency, source, evidence or transition conflict returns
no `LifecycleTransitionResult` and is surfaced by the later implementation for its HTTP
adapter to map to 409.

### Idempotency and payload identity

- Uniqueness is scoped by `(case_id, idempotency_key)` as frozen by W1-L2.
- Reuse is allowed only when every command fact matches the stored activity and evidence:
  event type, lane, effective/occurred time, actor/reviewer, confirmation, source/supersede
  references, canonical payload and the complete evidence-reference set.
- Same case/key with any mismatch is the blocking code
  `LIFECYCLE_IDEMPOTENCY_CONFLICT`; it performs no write and returns no result.
- Payload equality is canonical JSON equality, not Python mapping insertion order. The later
  append implementation serializes with
  `json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)`.
  JSON object keys must be strings; NaN, infinity and non-JSON values are invalid.
- Evidence-reference order does not affect identity. The later implementation compares a
  duplicate-free set sorted by
  `(case_id, evidence_kind, object_type, object_id, content_hash, captured_at)`; two entries
  with the same persisted link identity but different hash or capture time conflict.

### Validation and downstream boundary

- This contract module provides typed, immutable carriers only. Apart from native `StrEnum`
  construction and dataclass keyword/field enforcement, it performs no runtime validation.
- LC-ACTIVITY-APPEND owns non-empty identifiers, timestamp compatibility with
  `DateTime(timezone=False)`, canonical JSON, sequence allocation, source existence/same-case
  checks, evidence existence/same-case checks, idempotency reuse/conflict and revision update.
- LC-LEGACY-PROJECTION owns the approved one-way precedence, OA sequence input, retention of
  the existing non-null `Case.status`, and production of sorted `conflict_codes` when the
  projection is unknown, unverified or inconsistent.
- LC-APPLY-EVENT-SEAM owns orchestration and enforces that only a confirmed whitelisted
  `LIFECYCLE` rule may change the three axes; `DOCUMENT`, `FEE`, `NEEDS_REVIEW` and
  `LEGACY_UNVERIFIED` activities must retain identical previous/current projections.
- Later overlay contracts may reuse enum values and `LifecycleProjection` field semantics,
  but define their own read schemas. They must not mutate these command/result carriers or
  infer center changes from document/fee facts.
- No rule registry, transition matrix, legacy mapping, persistence operation, transaction
  Protocol, endpoint schema or UI label belongs in `lifecycle_contracts.py`.

### Frozen RED / GREEN contract

RED must import the module and require the exact nine-name `__all__`, exact `StrEnum` member
sets/values, and exact four dataclass shapes above; before implementation it fails because
the module is absent. GREEN must prove each dataclass is frozen, slotted and keyword-only,
has the exact ordered fields/annotations/defaults, rejects positional construction and
mutation, preserves explicit nullable values, and introduces no persistence/framework
imports or extra public interface.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-L1-CASE-LIFECYCLE-PROJECTION-CARRIER-20260712-01`
- `FPMS-V8-W1-L2-CASE-ACTIVITY-EVENT-CARRIER-20260712-01`
- `FPMS-V8-W1-L3-CASE-ACTIVITY-EVIDENCE-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): L1–L3

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-CONTRACTS-20260712-01.md`
- `backend/app/modules/cases/lifecycle_contracts.py`
- `backend/tests/test_v8_lifecycle_contracts.py`
- `artifacts/FPMS-V8-LC-CONTRACTS-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_contracts.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_contracts.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_contracts.py tests/test_v8_lifecycle_contracts.py && .venv/bin/ruff format app/modules/cases/lifecycle_contracts.py tests/test_v8_lifecycle_contracts.py && .venv/bin/ruff check app/modules/cases/lifecycle_contracts.py tests/test_v8_lifecycle_contracts.py`
- `git diff --check -- backend/app/modules/cases/lifecycle_contracts.py backend/tests/test_v8_lifecycle_contracts.py tasks/postdemo/v8/FPMS-V8-LC-CONTRACTS-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-LC-CONTRACTS-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LC-CONTRACTS-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-LC-CONTRACTS-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-LC-CONTRACTS-20260712-01` pass. Only then may this task be reported PASS.
