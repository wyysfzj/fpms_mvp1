# FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `166`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `653`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

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

Atomically confirm/revoke/reuse one frozen gate decision, supersede the former current row and reject idempotency/payload/current-identity conflicts; no commit.

## Ultra Contract Freeze — 2026-07-13

This section is authoritative for the High implementation of this task. It
narrows the V8 design and plan into one deterministic record-service contract;
it does not record a customer decision and does not activate a gated lane.

### Frozen public Python interface

`backend/app/modules/system/decision_gate_service.py` MUST define exactly these
public types and callable for this closure:

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy.orm import Session


class DecisionGateCode(str, Enum):
    FEE_APPLICATION_DRAFT = "DG-FEE-APPLICATION-DRAFT"
    FEE_GRANT_YEAR_DRAFT = "DG-FEE-GRANT-YEAR-DRAFT"
    FEE_FUTURE_ANNUITY = "DG-FEE-FUTURE-ANNUITY"
    GRANT_EVIDENCE_SOURCE = "DG-GRANT-EVIDENCE-SOURCE"
    GRANT_MANUAL_REVIEW = "DG-GRANT-MANUAL-REVIEW"
    PAYMENT_WORKBOOK = "DG-PAYMENT-WORKBOOK"
    SERVICE_RATE_VERSION = "DG-SERVICE-RATE-VERSION"
    LEGACY_FORM_CLASS = "DG-LEGACY-FORM-CLASS"


class DecisionGateStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    REVOKED = "REVOKED"


class DecisionGateRecordDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"


@dataclass(frozen=True)
class RecordDecisionGateCommand:
    gate_code: DecisionGateCode
    scope_key: str
    decision_value: str | None
    decision_status: DecisionGateStatus
    source_reference: str
    source_version: str
    confirmed_by: str
    effective_at: datetime
    idempotency_key: str
    expected_current_gate_id: str | None


@dataclass(frozen=True)
class DecisionGateRecordResult:
    gate_id: str
    gate_code: DecisionGateCode
    scope_key: str
    decision_value: str | None
    decision_status: DecisionGateStatus
    source_reference: str
    source_version: str
    confirmed_by: str
    effective_at: datetime
    supersedes_gate_id: str | None
    decision_snapshot: str
    idempotency_key: str
    current_identity_key: str | None
    disposition: DecisionGateRecordDisposition


def record_decision_gate(
    command: RecordDecisionGateCommand,
    transaction: Session,
) -> DecisionGateRecordResult:
    ...
```

All three enums and both dataclasses are exact public contracts. Do not add a
generic rule-engine abstraction, callback, repository protocol, alternate
command/result shape, async variant or service class in this task.

### Frozen gate, scope and value grammar

1. `gate_code` MUST be one of the eight `DecisionGateCode` members above. Raw
   strings, unknown codes and enum lookalikes fail; the service does not coerce
   them.
2. For the seven non-legacy gate codes, `scope_key` is exactly either:
   - `GLOBAL`; or
   - `case:<case-id>`, where `<case-id>` is 1–36 characters, contains no
     whitespace and no `|`, and is preserved exactly. This task performs only
     syntactic scope validation; it does not add a case foreign key or decide
     global-versus-case precedence.
3. For `DG-LEGACY-FORM-CLASS`, `scope_key` is exactly `form-001` through
   `form-022`, or `ALL-22`. `GLOBAL`, `case:*`, out-of-range form numbers and
   differently cased spellings fail.
4. No field is trimmed, case-folded or otherwise normalized. Required strings
   must already be canonical: non-empty, equal to their own `strip()` result,
   contain no NUL, and fit the carrier limits (`scope_key` 256,
   `source_reference` 512, `source_version` 128, `confirmed_by` 36,
   `idempotency_key` 128 and non-null `expected_current_gate_id` 36).
   A non-null `expected_current_gate_id` must additionally be the lowercase,
   hyphenated canonical text of a UUID; malformed text is a 400 input error,
   while a well-formed but stale UUID is a 409 current-identity conflict.
5. A `CONFIRMED` command requires a non-empty canonical `decision_value`.
   Except for legacy-form classification, this service deliberately treats the
   value as customer-controlled data and MUST NOT invent or validate a
   gate-specific policy vocabulary.
6. A scoped legacy-form confirmation accepts exactly `CURRENT_OFFICIAL`,
   `HISTORICAL` or `INTERNAL_ONLY`.
7. An `ALL-22` legacy-form confirmation requires `decision_value` to be the
   canonical JSON text of one object with exactly the 22 keys `form-001`
   through `form-022`; every value is exactly one of the three classifications
   in item 6. Canonical JSON means `json.dumps(value, ensure_ascii=False,
   sort_keys=True, separators=(",", ":"), allow_nan=False)` and exact byte-for-
   byte equality with the submitted text. A blanket value or incomplete map
   fails.
8. A `REVOKED` command requires `decision_value is None`. Revocation source,
   version, actor and effective time remain mandatory audit facts.
9. `effective_at` MUST be a timezone-naive `datetime`. It is preserved exactly.
   A future time is valid to record; the downstream read service, not this
   writer, fails closed until it becomes effective.
10. `confirmed_by` MUST resolve to an existing `t_user.id`. The historical
    column name is retained for both confirmation and revocation actors.

### Frozen canonical snapshot and identities

The service, never the caller, creates `decision_snapshot` with the canonical
JSON rule in item 7. The object passed to `json.dumps` is exactly:

```python
{
    "confirmed_by": command.confirmed_by,
    "decision_status": command.decision_status.value,
    "decision_value": command.decision_value,
    "effective_at": command.effective_at.isoformat(timespec="microseconds"),
    "expected_current_gate_id": command.expected_current_gate_id,
    "gate_code": command.gate_code.value,
    "scope_key": command.scope_key,
    "source_reference": command.source_reference,
    "source_version": command.source_version,
}
```

Stored text is sorted, compact canonical JSON; Python `None` becomes JSON
`null`. `idempotency_key`, generated row ID and database timestamps are not
snapshot members.

- The current identity is exactly
  `f"{command.gate_code.value}|{command.scope_key}"`.
- Exactly the current row stores that value; every superseded row stores
  `current_identity_key = None`.
- A created row receives an application-generated canonical UUID string.
- `supersedes_gate_id` is the prior current row ID, or `None` for the first
  confirmation. It MUST equal the command's non-null
  `expected_current_gate_id` whenever a prior current row exists.

### Frozen validation and database order

The implementation MUST use this observable order so a command with multiple
faults produces one deterministic error and no write:

1. Validate command instance, enum instances, then canonical strings in this
   field order: `scope_key`, `source_reference`, `source_version`,
   `confirmed_by`, `idempotency_key`, `expected_current_gate_id`.
2. Validate `effective_at`, gate/scope compatibility, status/value combination
   and the legacy-form value rules; then build the canonical snapshot and
   current identity.
3. Query `idempotency_key` before actor or current-row checks. An exact snapshot
   match returns the persisted row with `REUSED`, even if that row has since
   been superseded. A different snapshot fails with the idempotency conflict.
4. Verify the actor exists.
5. Read the current row by exact `current_identity_key` and enforce the frozen
   transition matrix below.
6. Within one `transaction.begin_nested()` savepoint, clear the former current
   row's identity and flush that update before inserting/flushing the new row.
   This ordering is required by SQLite's unique current identity.
7. Return the persisted row with `CREATED`. The service MUST call `flush()` but
   MUST NOT call outer `commit()` or outer `rollback()`.

### Frozen transition and reuse matrix

| Existing exact idempotency row | Current row | Command | Required result |
| --- | --- | --- | --- |
| Same snapshot | any, including no longer current | any | Return that row as `REUSED`; no mutation and no transition re-evaluation. |
| Different snapshot | any | any | 409 `DECISION_GATE_IDEMPOTENCY_PAYLOAD_CONFLICT`; no mutation. |
| None | None | `CONFIRMED`, expected current `None` | Create first current `CONFIRMED` row. |
| None | None | `CONFIRMED`, expected current non-null | 409 `DECISION_GATE_CURRENT_IDENTITY_CONFLICT`; no mutation. |
| None | None | `REVOKED` | 409 `DECISION_GATE_CURRENT_NOT_FOUND`; no mutation. |
| None | `CONFIRMED` | expected ID equals current ID; `CONFIRMED` | Supersede current with the new `CONFIRMED` row. A repeated value with a new idempotency key is a new auditable decision, not reuse. |
| None | `CONFIRMED` | expected ID equals current ID; `REVOKED` | Supersede current with a current `REVOKED` row. |
| None | `REVOKED` | expected ID equals current ID; `CONFIRMED` | Supersede revocation with a new current `CONFIRMED` row. |
| None | `REVOKED` | expected ID equals current ID; `REVOKED` | 409 `DECISION_GATE_ALREADY_REVOKED`; no mutation. |
| None | any current row | expected ID missing or different | 409 `DECISION_GATE_CURRENT_IDENTITY_CONFLICT`; no mutation. |

A `REVOKED` row remains the one current identity. It is not represented by
absence: downstream reads must be able to distinguish never recorded from
explicitly revoked.

### Frozen concurrency and SQLite behavior

- The unique `idempotency_key` and nullable unique `current_identity_key` are
  the concurrency authorities. Do not use `RETURNING`, database-specific locks,
  retry loops or process-local locks.
- Catch `IntegrityError` only around the nested savepoint. The savepoint must
  roll back its attempted old-row update and insert without rolling back the
  caller's outer transaction.
- After the savepoint rollback, re-read in this exact order:
  1. `idempotency_key`: matching snapshot returns the winner as `REUSED`;
     different snapshot raises the idempotency conflict.
  2. current identity: any winner not equal to the command's expected current
     state raises `DECISION_GATE_CURRENT_IDENTITY_CONFLICT`.
  3. if neither winner is visible, raise `DECISION_GATE_WRITE_CONFLICT`.
- A race path MUST NOT retry a mutation and MUST NOT silently replace the
  winning current row.

### Frozen BusinessError taxonomy and status mapping

The service uses `app.core.errors.BusinessError` via `raise_business_error`.
Messages may be concise English, but the following code/status/details contract
is exact:

| Error code | Status | Required condition | Required details |
| --- | --- | --- | --- |
| `DECISION_GATE_INVALID` | 400 | Invalid runtime type, canonical string, datetime, scope/status/value combination or legacy map | `{"field": "<field>"}` |
| `DECISION_GATE_ACTOR_NOT_FOUND` | 404 | Canonical `confirmed_by` does not identify a user | `{"confirmed_by": "<id>"}` |
| `DECISION_GATE_IDEMPOTENCY_PAYLOAD_CONFLICT` | 409 | Existing idempotency key has a different canonical snapshot | `{"idempotency_key": "<key>", "existing_gate_id": "<id>"}` |
| `DECISION_GATE_CURRENT_NOT_FOUND` | 409 | Revocation has no current row | `{"current_identity_key": "<identity>"}` |
| `DECISION_GATE_ALREADY_REVOKED` | 409 | A new revocation targets the matching current revoked row | `{"current_gate_id": "<id>"}` |
| `DECISION_GATE_CURRENT_IDENTITY_CONFLICT` | 409 | Expected current ID and stored current identity disagree, multiplicity is corrupt, or a current-identity race is won elsewhere | `{"current_identity_key": "<identity>", "expected_current_gate_id": <string-or-null>, "actual_current_gate_id": <string-or-null>}` |
| `DECISION_GATE_WRITE_CONFLICT` | 409 | Integrity race has neither a readable idempotency winner nor current-identity winner | `{"idempotency_key": "<key>", "current_identity_key": "<identity>"}` |

HTTP 422 belongs to the later Pydantic API schema and MUST NOT be invented by
this service. The later confirm API maps `CREATED` to 201 and `REUSED` to 200.

### Frozen RED / GREEN test contract

`backend/tests/test_v8_decision_gate_record_service.py` MUST prove all of the
following through the public interface:

1. Exact enum values, frozen dataclass field order/types and synchronous
   function signature.
2. First confirmation persists one current row, canonical snapshot, exact
   current identity, UUID and `CREATED`; it flushes and does not commit.
3. Exact replay returns the same row as `REUSED`, creates no row and performs no
   current-row mutation, both while current and after a later supersession.
4. Same idempotency key with any snapshot field changed returns the exact 409
   payload-conflict contract before actor/current validation.
5. Confirmation-over-confirmation, revocation-over-confirmation and
   confirmation-after-revocation clear the old current key, create one new
   current row and preserve the exact supersession chain.
6. First-action revocation, double revocation and missing/mismatched expected
   current IDs fail with their exact 409 contracts and no write.
7. Parameterized invalid inputs cover raw enum strings, each bounded/canonical
   string, aware/non-datetime effective time, illegal status/value combinations,
   non-legacy invalid scope and legacy invalid scope/value.
8. `form-001`, `form-022` and the complete canonical `ALL-22` map pass; an
   incomplete, extra-key, blanket, non-canonical or illegal-value map fails.
9. A missing actor returns the exact 404 contract without changing current
   identity.
10. Simulated unique-idempotency and unique-current-identity races exercise the
    savepoint re-read branches: exact winner reuse, payload conflict, current
    conflict and generic write conflict; the outer transaction is not committed
    or rolled back by the service.
11. The inherited carrier regression
    `backend/tests/test_v8_customer_decision_gate_schema.py` remains green.

The RED is the missing public service contract/behavior, not a deliberately
malformed fixture. GREEN does not require the later read service or HTTP API.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): carrier

### Shared ownership serialization

- `backend/app/modules/system/decision_gate_service.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01.md`
- `backend/app/modules/system/decision_gate_service.py`
- `backend/tests/test_v8_decision_gate_record_service.py`
- `artifacts/FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_record_service.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_record_service.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_customer_decision_gate_schema.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_record_service.py && .venv/bin/ruff format app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_record_service.py && .venv/bin/ruff check app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_record_service.py`
- `git diff --check -- backend/app/modules/system/decision_gate_service.py backend/tests/test_v8_decision_gate_record_service.py tasks/postdemo/v8/FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01` pass. Only then may this task be reported PASS.
