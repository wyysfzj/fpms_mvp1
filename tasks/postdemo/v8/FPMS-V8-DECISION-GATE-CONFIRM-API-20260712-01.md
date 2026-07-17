# FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `168`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `655`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-API`

- RED expectation: Exact API test fails because the sole route, strict schemas, actor ownership, disposition status mapping or transaction boundary is missing.
- GREEN expectation: Exact API test passes the direct full response, 201/200 disposition mapping, 400/401/403/404/409/422 matrix and no-second-route contract.

## Exact Closure Slice

Exactly one `POST /api/v1/system/decision-gates` endpoint using `SystemParam.Edit` records confirmation, revocation or post-revocation reconfirmation through the accepted record service and returns its full direct result as 201 `CREATED` or 200 `REUSED`.

## Ultra Contract Freeze — 2026-07-14

This section is authoritative for High implementation. It materializes section 4 of
`docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
without widening this task beyond one HTTP adapter.

### Frozen route, permission and request

The sole route is:

```text
POST /api/v1/system/decision-gates
```

The same resource-collection endpoint accepts `decision_status=CONFIRMED` for first
confirmation or reconfirmation and `decision_status=REVOKED` for revocation. A
`CONFIRMED` request targeting the current revoked row is the only reconfirmation path.
Do not add `/confirm`, `/revoke` or any other second route. Preserve parameter-injected
`SystemParam.Edit` permission enforcement and obtain the authenticated actor through
`current_user_dep`.

`DecisionGateRecordIn` is strict with `ConfigDict(extra="forbid")` and has exactly these
fields in this order:

```python
gate_code: DecisionGateCode
scope_key: str
decision_value: str | None
decision_status: DecisionGateStatus
source_reference: str
source_version: str
effective_at: datetime
idempotency_key: str
expected_current_gate_id: str | None
```

All nine fields are required. In particular, `decision_value` and
`expected_current_gate_id` are nullable but have no defaults and therefore may not be
omitted. `confirmed_by` is not a request field: the API supplies
`current_user.id`, and a client-supplied `confirmed_by` is an extra field that returns
422. The schema owns only JSON shape, type, enum and datetime parsing. Scope, value,
canonical-string and naive-datetime business validation remain exclusively in the
accepted record service and retain its deterministic 400 validation order.

### Frozen direct response and status mapping

`DecisionGateRecordOut` has no success envelope and mirrors the accepted
`DecisionGateRecordResult` exactly in this field order and with these annotations:

```python
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
```

An accepted result with `disposition=CREATED` returns 201. An accepted result with
`disposition=REUSED` returns 200, with the full body and `gate_id` unchanged from the
persisted replay result.

### Frozen adapter and transaction boundary

The API constructs one `RecordDecisionGateCommand` from the nine request fields plus
server-owned `confirmed_by=current_user.id`, then calls
`record_decision_gate(command, db)`. It does not duplicate any gate, scope, transition,
idempotency or canonicalization rule.

After an accepted service result, the API calls `db.commit()` exactly once, including
for `REUSED`, and returns the direct output with the disposition-selected HTTP status.
A service `BusinessError` triggers one `db.rollback()` and is re-raised unchanged. A
commit failure triggers one `db.rollback()` and the original failure is re-raised. The
API does not refresh, issue a second SELECT, retry, mutate the accepted result or perform
a second business write.

### Frozen HTTP error matrix

| Status | Exact API behavior |
| --- | --- |
| 400 | Pass through record-service `DECISION_GATE_INVALID` unchanged. |
| 401 | Existing authentication dependency rejects a missing or invalid authenticated user. |
| 403 | Parameter-injected `SystemParam.Edit` permission dependency rejects the caller. |
| 404 | `DECISION_GATE_ACTOR_NOT_FOUND` is not expected after normal authentication, but an authenticated-user deletion race is passed through unchanged. |
| 409 | Pass through `DECISION_GATE_IDEMPOTENCY_PAYLOAD_CONFLICT`, `DECISION_GATE_CURRENT_NOT_FOUND`, `DECISION_GATE_ALREADY_REVOKED`, `DECISION_GATE_CURRENT_IDENTITY_CONFLICT` and `DECISION_GATE_WRITE_CONFLICT` unchanged. |
| 422 | Request validation only: missing required fields, extra fields, or JSON type/enum/datetime parsing failures. |

The API does not remap service `BusinessError` codes, statuses or details.

### Frozen RED / GREEN test contract

The exact RED is the missing route/schema/adapter behavior, not a deliberately malformed
fixture. `backend/tests/test_v8_decision_gate_confirm_api.py` must prove:

1. the sole route, `SystemParam.Edit` parameter injection and authenticated server-owned
   actor;
2. exact input/output field names, order and annotations, strict extras, and required
   nullable fields;
3. first confirmation, revocation and post-revocation reconfirmation all dispatch through
   the same endpoint and accepted record service;
4. 201/full `CREATED` and 200/full unchanged `REUSED` responses with no success envelope;
5. exactly one commit on each accepted disposition, rollback on service `BusinessError`
   and commit failure, and no refresh or second SELECT;
6. the exact 400/401/403/404/409/422 matrix and absence of `/confirm` and `/revoke`
   routes.

GREEN requires only this exact API test and the task-scoped checks listed below; it does
not absorb a second endpoint or an inherited regression suite.

## Explicit Non-Closure

No second endpoint (including `/confirm` or `/revoke`), router rewiring, business-rule duplication or frontend work. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): record service

### Shared ownership serialization

- `backend/app/modules/system/api.py` order key `1`; project this order only across owners present in the active manifest.
- `backend/app/modules/system/decision_gate_schemas.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01.md`
- `backend/app/modules/system/decision_gate_schemas.py`
- `backend/app/modules/system/api.py`
- `backend/tests/test_v8_decision_gate_confirm_api.py`
- `artifacts/FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_confirm_api.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_confirm_api.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_confirm_api.py && .venv/bin/ruff format app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_confirm_api.py && .venv/bin/ruff check app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_confirm_api.py`
- `git diff --check -- backend/app/modules/system/decision_gate_schemas.py backend/app/modules/system/api.py backend/tests/test_v8_decision_gate_confirm_api.py tasks/postdemo/v8/FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01` pass. Only then may this task be reported PASS.
