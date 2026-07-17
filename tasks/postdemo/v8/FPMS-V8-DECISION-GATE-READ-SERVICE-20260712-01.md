# FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `167`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `654`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: medium
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-SERVICE`

- RED expectation: Exact service/dataset test fails on missing behavior, data or prohibited side effect.
- GREEN expectation: Exact service/dataset test and named inherited regressions pass with caller-owned transaction semantics where writes are transactional.

## Exact Closure Slice

Resolve exactly one current effective global/case/form decision and fail closed on absence, revocation, future date, scope mismatch or corrupt multiplicity.

## Ultra Contract Freeze — 2026-07-13

This section is the complete High implementation contract for this one read
service. It narrows the V8 design and plan without recording a decision,
activating a customer-dependent lane or changing the existing record service.

### Frozen public Python interface

`backend/app/modules/system/decision_gate_service.py` MUST reuse the already
frozen `DecisionGateCode` enum from the record-service task and add exactly
these public DTOs and callable for this closure:

```python
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolveDecisionGateCommand:
    gate_code: DecisionGateCode
    scope_key: str
    as_of: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class DecisionGateReadResult:
    gate_id: str
    gate_code: DecisionGateCode
    requested_scope_key: str
    resolved_scope_key: str
    decision_value: str
    source_reference: str
    source_version: str
    confirmed_by: str
    effective_at: datetime


def resolve_decision_gate(
    command: ResolveDecisionGateCommand,
    transaction: Session,
) -> DecisionGateReadResult:
    ...
```

The dataclass field names, order and annotations and the synchronous function
signature are exact. The command and result are frozen, slotted and
keyword-only. Do not duplicate or widen `DecisionGateCode`, return an ORM row,
add an async/service-class/repository abstraction or add a fallback flag;
fallback is represented exactly by differing `requested_scope_key` and
`resolved_scope_key` values.

### Frozen command grammar

Validation completes before any SELECT and uses 400 `DECISION_GATE_INVALID`
with exact details `{"field": "<field>"}`:

1. `command` MUST have exact runtime type `ResolveDecisionGateCommand`.
2. `gate_code` MUST have exact runtime type `DecisionGateCode`; raw strings,
   unknown values and enum lookalikes are not coerced.
3. For each non-legacy gate, `scope_key` is exactly `GLOBAL` or
   `case:<case-id>`. The case ID is 1-36 characters, contains no whitespace and
   no `|`, and is preserved byte-for-byte.
4. For `DG-LEGACY-FORM-CLASS`, the public request scope is exactly `form-001`
   through `form-022`. `ALL-22`, `GLOBAL`, `case:*`, differently cased values
   and out-of-range forms are invalid. `ALL-22` is persistence-only fallback
   data, never a public single-decision request.
5. No scope is trimmed, case-folded or normalized. A non-string scope, NUL,
   surrounding whitespace or malformed grammar fails on `scope_key`.
6. `as_of` MUST have exact runtime type `datetime` and be timezone-naive
   (`utcoffset() is None`). It is caller supplied and preserved exactly;
   non-datetime and aware values fail on `as_of`.

Validation order is exactly `command`, `gate_code`, `scope_key`, `as_of`.
This service does not validate a case, actor or source by a second query and
does not read a clock.

### Frozen candidate query and precedence

After validation, construct current-identity candidates in this exact order:

| Request | More-specific identity | Fallback identity |
| --- | --- | --- |
| non-legacy `GLOBAL` | `<gate-code>|GLOBAL` | none |
| non-legacy `case:<id>` | `<gate-code>|case:<id>` | `<gate-code>|GLOBAL` |
| legacy `form-NNN` | `DG-LEGACY-FORM-CLASS|form-NNN` | `DG-LEGACY-FORM-CLASS|ALL-22` |

Issue exactly one SELECT against `CustomerDecisionGate.current_identity_key`
using the complete candidate set. Retrieve all matching rows in that one
result; do not issue a direct query followed by a fallback query. Superseded
rows have a null current identity and are never queried or revived.

For each candidate identity, zero or one row is valid. More than one row for
either identity is corrupt multiplicity and fails before selection. One row
for each of the two different identities is valid and is not multiplicity.
Then apply this exact precedence:

| More-specific row | Fallback row | Required behavior |
| --- | --- | --- |
| present | any | Select the more-specific row; fallback status/value/effective time is not interpreted. |
| absent | present | Select the fallback row. |
| absent | absent | 409 `DECISION_GATE_NOT_FOUND`. |

Presence shadows fallback before status, effective-time or value validation.
Therefore a more-specific current row that is `REVOKED`, future-effective or
corrupt MUST produce its own fail-closed error and MUST NOT fall through to a
valid confirmed fallback.

### Frozen selected-row and `as_of` semantics

Validate the selected row in this exact order:

1. Its `gate_code`, `scope_key` and `current_identity_key` must exactly match
   the selected candidate identity. No component is reconstructed, repaired or
   inferred.
2. `REVOKED` fails closed. Any stored status other than exact `CONFIRMED` or
   `REVOKED` is corrupt.
3. `effective_at` must be an exact naive `datetime`. The row is effective only
   when `effective_at <= command.as_of`; equality is effective.
4. A non-legacy confirmed decision value must be a non-empty string equal to
   its own `strip()` value and contain no NUL.
5. A direct legacy `form-NNN` value must be exactly `CURRENT_OFFICIAL`,
   `HISTORICAL` or `INTERNAL_ONLY`.
6. A selected `ALL-22` fallback value must be byte-for-byte canonical JSON
   produced with
   `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)`.
   It must be one object with exactly all 22 keys `form-001..form-022`, and
   every value must be one of the three classifications in item 5. Return only
   the requested form's classification as `decision_value`; return `ALL-22` as
   `resolved_scope_key` and the requested `form-NNN` unchanged as
   `requested_scope_key`.

`as_of` tests only whether the one selected current row is effective. It is not
a bitemporal or audit-history query: no supersession traversal, no
`recorded_at` reconstruction and no lookup of an older confirmed row is
allowed. A future-effective current row shadows and does not revive an older
confirmed row. Successful results project the selected row's exact ID, source,
version, actor and effective time; the service infers no business state from
the opaque decision value.

### Frozen BusinessError taxonomy and evaluation order

The service uses `app.core.errors.BusinessError` via `raise_business_error`.
Messages may be concise English, but code, status and details are exact:

| Error code | Status | Required condition | Exact details |
| --- | --- | --- | --- |
| `DECISION_GATE_INVALID` | 400 | Invalid command, enum, scope or `as_of` | `{"field": "<field>"}` |
| `DECISION_GATE_CANDIDATE_MULTIPLICITY` | 409 | More than one row has one exact candidate current identity | `{"current_identity_key": "<identity>", "candidate_count": <int>}` |
| `DECISION_GATE_NOT_FOUND` | 409 | No more-specific or fallback current row exists | `{"gate_code": "<gate-code>", "scope_key": "<requested-scope>"}` |
| `DECISION_GATE_CURRENT_IDENTITY_CONFLICT` | 409 | Selected row's gate, scope or current identity disagrees with the selected candidate | `{"gate_id": "<id>", "expected_current_identity_key": "<identity>", "actual_current_identity_key": <string-or-null>, "actual_gate_code": "<stored-value>", "actual_scope_key": "<stored-value>"}` |
| `DECISION_GATE_REVOKED` | 409 | Selected row is exactly `REVOKED` | `{"gate_id": "<id>", "resolved_scope_key": "<scope>"}` |
| `DECISION_GATE_CURRENT_ROW_CORRUPT` | 409 | Selected status, effective time, or non-map decision value violates this contract | `{"gate_id": "<id>", "field": "<field>"}` |
| `DECISION_GATE_NOT_EFFECTIVE` | 409 | Selected confirmed current row has `effective_at > as_of` | `{"gate_id": "<id>", "effective_at": "<microsecond-ISO>", "as_of": "<microsecond-ISO>"}` |
| `DECISION_GATE_LEGACY_MAP_CORRUPT` | 409 | Selected `ALL-22` JSON is invalid, non-canonical, incomplete, over-complete or contains an illegal value | `{"gate_id": "<id>", "scope_key": "ALL-22"}` |

For identity-conflict details, persisted string values are emitted unchanged;
a null current identity remains JSON null. Datetimes in details use
`isoformat(timespec="microseconds")`.

After command validation and the single SELECT, evaluation order is exactly:
candidate multiplicity in candidate precedence order; absence; selected-row
identity; status; stored `effective_at` shape; future effectiveness; decision
value. A corrupt direct legacy value uses
`DECISION_GATE_CURRENT_ROW_CORRUPT` with field `decision_value`; only the
selected `ALL-22` carrier uses `DECISION_GATE_LEGACY_MAP_CORRUPT`.

### Frozen read-only transaction boundary and serialization

- A valid invocation executes exactly one SELECT and performs no INSERT,
  UPDATE or DELETE. An invalid command executes no SQL.
- The service MUST NOT call `add`, `flush`, `commit`, `rollback`,
  `begin_nested`, refresh or close, and MUST NOT mutate a returned ORM row.
- It MUST NOT use a system clock, case/user lookup, row lock, retry, fallback
  provider, gate-specific policy map or status inference.
- The prerequisite record-service task retains shared-file order key `1` and
  this task retains order key `2` for
  `backend/app/modules/system/decision_gate_service.py`. Its implementation and
  verification begin only after the record service is accepted; the two owners
  never edit or verify this shared file concurrently.
- The record service's enums, writer DTOs, callable, error behavior and
  caller-owned savepoint semantics remain unchanged. This task adds only the
  read DTOs, read helpers and read callable.

### Frozen RED / GREEN test matrix

`backend/tests/test_v8_decision_gate_read_service.py` MUST prove through the
public seam:

1. Exact reused enum identity, frozen/slotted/keyword-only DTO field
   names/order/types and synchronous function signature.
2. Exact 400 validation and field order for wrong command, raw enum, every
   invalid non-legacy/legacy scope and non-datetime/aware `as_of`; invalid input
   performs no SELECT.
3. A non-legacy `GLOBAL` request resolves only the exact global row and returns
   the exact result/provenance projection.
4. A non-legacy case request falls back to `GLOBAL` only when no case current
   row exists; a valid case row wins when both rows exist.
5. Case rows that are revoked, future-effective or corrupt each return their
   exact 409 and never use a confirmed global fallback.
6. `form-001` and `form-022` each resolve direct classifications and extract
   their exact value from a valid canonical `ALL-22` fallback when direct is
   absent; requesting `ALL-22` itself is 400.
7. A revoked, future-effective or corrupt direct form row shadows a valid
   `ALL-22` carrier and returns its exact 409.
8. Missing candidates, selected-row identity mismatch, and duplicate rows for
   either exact candidate identity return their exact 409 details. One direct
   plus one fallback row is not multiplicity.
9. Invalid JSON, non-canonical JSON, missing/extra form keys, blanket values,
   non-string values and illegal classifications each return exact 409
   `DECISION_GATE_LEGACY_MAP_CORRUPT`.
10. `effective_at == as_of` succeeds; one microsecond before effectiveness
    fails; a future current row never revives a superseded confirmed row.
11. A transaction spy proves one SELECT for every valid success/error path and
    zero calls to mutation, transaction-boundary or clock-dependent behavior.
12. The inherited record-service and carrier regressions remain green without
    changing their public contracts.

The RED is the missing read DTO/callable/behavior, not a malformed test fixture.
GREEN does not require an endpoint, audit-list API, lane activation or customer
decision.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): record service; serialized

### Shared ownership serialization

- `backend/app/modules/system/decision_gate_service.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01.md`
- `backend/app/modules/system/decision_gate_service.py`
- `backend/tests/test_v8_decision_gate_read_service.py`
- `artifacts/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_read_service.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_read_service.py tests/test_v8_decision_gate_record_service.py tests/test_v8_customer_decision_gate_schema.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_read_service.py && .venv/bin/ruff format app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_read_service.py && .venv/bin/ruff check app/modules/system/decision_gate_service.py tests/test_v8_decision_gate_read_service.py`
- `git diff --check -- backend/app/modules/system/decision_gate_service.py backend/tests/test_v8_decision_gate_read_service.py tasks/postdemo/v8/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01` pass. Only then may this task be reported PASS.
