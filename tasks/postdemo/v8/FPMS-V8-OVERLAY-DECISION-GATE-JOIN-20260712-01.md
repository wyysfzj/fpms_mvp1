# FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `16. Wave 7 — lifecycle overlay and centered UI`
Catalog ordinal: `263`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `794`
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

- RED expectation: Exact overlay test fails because the ordered 29-entry decision-gate join, composite identity or fail-closed error mapping is missing.
- GREEN expectation: Exact overlay test passes the 29-call/order/scope/timestamp/transaction, resolved/unresolved projection and no-activation/no-write contract.

## Exact Closure Slice

Join the accepted decision-gate read service into one lifecycle-overlay invocation to return exactly 29 ordered, composite-identified gate entries, including independent unresolved reasons, without activating a lane or altering any business state.

## Ultra Contract Freeze — 2026-07-14

This section is authoritative for High implementation. It materializes the approved
delta-2 decision-gate join only; it does not redefine the accepted read service, add a
second dataset or change lifecycle, document or fee behavior.

### Frozen ordered entry set and identity

Each overlay invocation returns exactly 29 `OverlayDecisionGate` entries covering eight
distinct `DecisionGateCode` values. Build and resolve them in this exact order:

1. `DG-FEE-APPLICATION-DRAFT` with `requested_scope_key=f"case:{case_id}"`.
2. `DG-FEE-GRANT-YEAR-DRAFT` with `requested_scope_key=f"case:{case_id}"`.
3. `DG-FEE-FUTURE-ANNUITY` with `requested_scope_key=f"case:{case_id}"`.
4. `DG-GRANT-EVIDENCE-SOURCE` with `requested_scope_key=f"case:{case_id}"`.
5. `DG-GRANT-MANUAL-REVIEW` with `requested_scope_key=f"case:{case_id}"`.
6. `DG-PAYMENT-WORKBOOK` with `requested_scope_key=f"case:{case_id}"`.
7. `DG-SERVICE-RATE-VERSION` with `requested_scope_key=f"case:{case_id}"`.
8. `DG-LEGACY-FORM-CLASS` repeated 22 times with requested scopes in ascending
   `form-001` through `form-022` order.

Entry identity is exactly `(gate_code, requested_scope_key)`. The legacy gate code is
therefore intentionally repeated; neither this service nor a caller may key, deduplicate
or replace entries by gate code alone. The returned tuple preserves the resolver-request
order above even when entries are unresolved.

The join MUST never call the resolver with `scope_key="ALL-22"` and MUST never output an
entry whose `requested_scope_key` is `ALL-22`. A legacy resolver fallback preserves the
requested `form-NNN` in `requested_scope_key`, reports `ALL-22` only in
`resolved_scope_key`, and projects the exact extracted value and source provenance from
the accepted read result.

### Frozen timestamp, resolver and transaction boundary

- Capture one timezone-naive UTC `generated_at` for the whole overlay invocation. Its
  `utcoffset()` is `None`; return that value as `LifecycleOverlay.generated_at` and pass
  the same value unchanged as `ResolveDecisionGateCommand.as_of` for all 29 entries.
- For every ordered identity above, construct one accepted
  `ResolveDecisionGateCommand` and call `resolve_decision_gate(command, transaction)`
  with the exact caller-owned `Session` used by the overlay invocation.
- A fully projected invocation makes exactly 29 resolver calls, including when any
  number of entries produce the independently mappable 409 results below. Calls follow
  the frozen entry order. An invocation never makes more than 29 resolver calls, never
  retries one entry and never performs a separate `ALL-22` lookup.
- Scope precedence and fallback selection remain exclusively inside the accepted read
  service. The join MUST NOT query decision-gate rows directly, copy the resolver's
  precedence, introduce a blanket fallback or open a second transaction.
- This join is read-only: it performs no add/flush/commit/rollback, gate record, lane
  activation, lifecycle transition, fee/document mutation or other business write.

### Frozen resolved and unresolved projection

For a successful read result, produce one `OverlayDecisionGate` with:

```text
gate_code = result.gate_code
requested_scope_key = result.requested_scope_key
resolution_status = RESOLVED
gate_id = result.gate_id
resolved_scope_key = result.resolved_scope_key
decision_value = result.decision_value
source_reference = result.source_reference
source_version = result.source_version
confirmed_by = result.confirmed_by
effective_at = result.effective_at
unresolved_reason = None
```

Map only these exact read-service 409 codes independently to `UNRESOLVED`:

```text
DECISION_GATE_NOT_FOUND
DECISION_GATE_REVOKED
DECISION_GATE_NOT_EFFECTIVE
DECISION_GATE_CANDIDATE_MULTIPLICITY
DECISION_GATE_CURRENT_IDENTITY_CONFLICT
DECISION_GATE_CURRENT_ROW_CORRUPT
DECISION_GATE_LEGACY_MAP_CORRUPT
```

The unresolved entry retains the attempted `gate_code` and exact
`requested_scope_key`, uses the error code unchanged as `unresolved_reason`, and sets
`gate_id`, `resolved_scope_key`, `decision_value`, `source_reference`, `source_version`,
`confirmed_by` and `effective_at` all to `None`. It does not stop or alter resolution of
the other 28 entries or any lifecycle/document/fee projection.

An internal read-service 400 `DECISION_GATE_INVALID` indicates a join contract defect.
Fail the whole overlay request as 409
`LIFECYCLE_OVERLAY_DECISION_GATE_CONTRACT_INVALID`; do not return a partial overlay or
convert it to an unresolved entry. Every other error, including an unexpected status for
one of the named codes, propagates unchanged. Do not add a blanket exception-to-
unresolved path.

`HISTORICAL` and `INTERNAL_ONLY` are source-backed `RESOLVED` legacy classifications and
remain reference-only. Only `CURRENT_OFFICIAL` is eligible for later corresponding-form
lane activation. This join activates nothing, including for `CURRENT_OFFICIAL`, and does
not reinterpret or rewrite any of the three decision values.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-OVERLAY-FEE-JOIN-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): fee join; decision-gate read service

### Shared ownership serialization

- `backend/app/modules/cases/lifecycle_overlay_service.py` order key `4`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01.md`
- `backend/app/modules/cases/lifecycle_overlay_service.py`
- `backend/tests/test_v8_lifecycle_overlay_decision_gates.py`
- `artifacts/FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Exact TDD Acceptance Matrix

`backend/tests/test_v8_lifecycle_overlay_decision_gates.py` MUST prove through the
public overlay seam:

1. One invocation returns exactly 29 entries in the frozen order: the seven exact
   non-legacy codes at `case:{case_id}`, followed by 22 repeated legacy-code entries at
   ascending `form-001..form-022`; all identities are the composite pair.
2. A resolver spy receives exactly those 29 commands in order, never receives
   `ALL-22`, receives the same caller `Session` every time and is never called more than
   29 times.
3. One captured timezone-naive UTC value is both the returned `generated_at` and every
   command's exact `as_of`; the join does not read a new clock value per entry.
4. Direct non-legacy and legacy successes project every result field losslessly with
   `RESOLVED` and null `unresolved_reason`.
5. A legacy `ALL-22` fallback result keeps requested `form-NNN`, reports resolved
   `ALL-22`, and preserves the exact extracted classification and source fields without
   ever outputting requested scope `ALL-22`.
6. Parameterize each of the seven exact read-service 409 codes at the first, middle and
   final entry. Only that entry becomes `UNRESOLVED`, its reason is the unchanged code,
   all seven nullable record/source fields are `None`, the other 28 entries remain
   intact and all 29 resolutions complete.
7. Multiple independently mappable 409 results in one invocation retain their own
   composite identities/reasons and do not block lifecycle, document or fee data.
8. Internal 400 `DECISION_GATE_INVALID` fails the whole invocation with exact 409
   `LIFECYCLE_OVERLAY_DECISION_GATE_CONTRACT_INVALID`, returns no partial overlay and
   performs no later resolver call.
9. Any other `BusinessError` or non-business exception propagates unchanged, is not
   projected as unresolved and performs no retry or later resolver call.
10. `CURRENT_OFFICIAL`, `HISTORICAL` and `INTERNAL_ONLY` all project as source-backed
    `RESOLVED`; the latter two remain reference-only, and a transaction/side-effect spy
    proves that none of the three activates a lane or performs a write.

The RED is the missing 29-entry join behavior, not malformed fixtures. GREEN does not
require the later keyset, HTTP or frontend tasks and does not record customer decisions.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_decision_gates.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_overlay_decision_gates.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_decision_gates.py && .venv/bin/ruff format app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_decision_gates.py && .venv/bin/ruff check app/modules/cases/lifecycle_overlay_service.py tests/test_v8_lifecycle_overlay_decision_gates.py`
- `git diff --check -- backend/app/modules/cases/lifecycle_overlay_service.py backend/tests/test_v8_lifecycle_overlay_decision_gates.py tasks/postdemo/v8/FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01` pass. Only then may this task be reported PASS.
