# FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `108`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `536`
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

- RED expectation: Exact API test fails because the sole route, strict schemas, actor
  ownership, direct replay response or transaction boundary is missing.
- GREEN expectation: Exact API test passes the direct 200 success/replay response, exact
  400/401/403/404/409/422 matrix and no-second-route contract.

## Exact Closure Slice

One POST obligation-instruction endpoint using `Fee.Edit`; 200 idempotent, 409 non-actionable/conflicting instruction and no draft side effect.

## Ultra Contract Freeze — 2026-07-14

This section is authoritative for High implementation. It materializes section 5 of
`docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
without widening this task beyond one HTTP adapter.

### Frozen route, permission and request

The sole route is:

```text
POST /api/v1/fees/obligations/{obligation_id}/instruction
```

`obligation_id` is a required `str` path parameter and appears nowhere in the request
body. Preserve parameter-injected `Fee.Edit` permission enforcement and obtain the
authenticated actor through `current_user_dep`.

`FeeObligationInstructionIn` is strict with `ConfigDict(extra="forbid")` and has exactly
these required fields in this order:

```python
instruction: FeeClientInstruction  # PAY | HOLD | ABANDON
idempotency_key: str
```

`actor_id` is not a request field: the API supplies `current_user.id`. Client-supplied
`obligation_id`, `actor_id` or any other extra field returns 422. The schema owns only JSON
shape, type and enum validation; well-typed business-invalid values remain the accepted
service's 400/409 responsibility. Do not add a collection-action route, a legacy request
shape or any overload.

### Frozen direct response and 200 semantics

`FeeObligationInstructionOut` has no success envelope and has exactly these fields in this
order:

```python
obligation_id: str
client_instruction_status: FeeClientInstructionStatus
activity_id: str
idempotency_key: str
reused: bool
```

Map `obligation_id` and `client_instruction_status` from
`result.obligation.id` and `result.obligation.statuses.client_instruction_status`; map the
other three fields directly from the accepted `RecordFeeObligationInstructionResult`.
Both a new accepted instruction (`reused=False`) and an exact replay (`reused=True`) return
200. An exact replay preserves the service-returned activity ID, idempotency key and current
instruction status.

### Frozen adapter and transaction boundary

Construct one `RecordFeeObligationInstructionCommand` from the path ID, the two request
fields and server-owned `actor_id=current_user.id`, then call
`record_client_instruction(command, db)` exactly once. The adapter does not duplicate
eligibility, transition, replay, idempotency, concurrency or stored-state rules.

After any accepted service result, including `reused=True`, call `db.commit()` exactly once
and return the direct output. A service `BusinessError` triggers one `db.rollback()` and is
re-raised unchanged. A commit failure triggers one `db.rollback()` and the original failure
is re-raised. Do not refresh, issue a second SELECT, retry or perform a second business
write. In particular, the adapter must not create or modify a draft, PayList, payment,
official-payment evidence or case lifecycle/legal state.

### Frozen HTTP error matrix

| Status | Exact API behavior |
| --- | --- |
| 400 | Pass through service business validation, including `FEE_CLIENT_INSTRUCTION_COMMAND_INVALID`, unchanged. |
| 401 | Existing authentication dependency rejects a missing or invalid authenticated user. |
| 403 | Parameter-injected `Fee.Edit` permission dependency rejects the caller. |
| 404 | Pass through the accepted service's missing-obligation result, including `FEE_OBLIGATION_NOT_FOUND`, unchanged. |
| 409 | Pass through non-actionable/stored-state, same-state-new-key, idempotency, current-state and concurrency conflicts unchanged. |
| 422 | Request validation only: invalid path/body shape, missing fields, extra fields or invalid `instruction` enum. |

The API does not remap any service `BusinessError` code, message, details or status.

### Frozen RED / GREEN test contract

The exact RED is the missing route/schema/adapter behavior, not a deliberately malformed
fixture. `backend/tests/test_v8_fee_obligation_instruction_api.py` must prove:

1. the sole path-ID route, parameter-injected `Fee.Edit` permission and authenticated
   server-owned actor;
2. exact input/output field names, order and annotations, strict extras, path-only
   `obligation_id` and the exact `PAY/HOLD/ABANDON` enum;
3. one exact command projection and exactly one call to the already accepted
   `record_client_instruction()` seam, with no draft, PayList, payment or legal-state write;
4. direct five-field 200 responses for both new success and exact replay, preserving the
   service-returned replay facts;
5. exactly one commit for each accepted result, rollback on service `BusinessError` and
   commit failure, and no refresh, second SELECT or retry; and
6. the exact 400/401/403/404/409/422 matrix, absence of a collection-action/second route,
   and rejection of the legacy body-ID/actor request shape.

RED and GREEN execute only this exact API test. GREEN then runs only the task-scoped Ruff,
whitespace, task gate and evidence checks listed below; no inherited or broader product
suite is part of this task's RED/GREEN.

## Explicit Non-Closure

No second endpoint, router rewiring, business-rule duplication or frontend work. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): client instruction

### Shared ownership serialization

- `backend/app/modules/fees/api.py` order key `4`; project this order only across owners present in the active manifest.
- `backend/app/modules/fees/obligation_schemas.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01.md`
- `backend/app/modules/fees/obligation_schemas.py`
- `backend/app/modules/fees/api.py`
- `backend/tests/test_v8_fee_obligation_instruction_api.py`
- `artifacts/FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_instruction_api.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_obligation_instruction_api.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/obligation_schemas.py app/modules/fees/api.py tests/test_v8_fee_obligation_instruction_api.py && .venv/bin/ruff format app/modules/fees/obligation_schemas.py app/modules/fees/api.py tests/test_v8_fee_obligation_instruction_api.py && .venv/bin/ruff check app/modules/fees/obligation_schemas.py app/modules/fees/api.py tests/test_v8_fee_obligation_instruction_api.py`
- `git diff --check -- backend/app/modules/fees/obligation_schemas.py backend/app/modules/fees/api.py backend/tests/test_v8_fee_obligation_instruction_api.py tasks/postdemo/v8/FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FO-INSTRUCTION-HTTP-20260712-01` pass. Only then may this task be reported PASS.
