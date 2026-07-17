# FPMS-V8-DECISION-GATE-LIST-API-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `14. Wave 6 — customer decision gates`
Catalog ordinal: `169`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `656`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-API`

- RED expectation: Exact API test fails with route/shape/permission/status mismatch.
- GREEN expectation: Exact API test passes named 200/201/400/401/403/404/409/422 semantics and response envelope.

## Exact Closure Slice

One bodyless GET audit endpoint using `SystemParam.Read`, returning persisted source/version/scope/status without interpreting business behavior.

## Explicit Non-Closure

No second endpoint, router rewiring, business-rule duplication or frontend work. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01`
- `FPMS-V8-DECISION-GATE-CONFIRM-API-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): read service; serialized after confirm API

### Shared ownership serialization

- `backend/app/modules/system/api.py` order key `2`; project this order only across owners present in the active manifest.
- `backend/app/modules/system/decision_gate_schemas.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DECISION-GATE-LIST-API-20260712-01.md`
- `backend/app/modules/system/decision_gate_schemas.py`
- `backend/app/modules/system/api.py`
- `backend/tests/test_v8_decision_gate_list_api.py`
- `artifacts/FPMS-V8-DECISION-GATE-LIST-API-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_list_api.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_decision_gate_list_api.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_list_api.py && .venv/bin/ruff format app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_list_api.py && .venv/bin/ruff check app/modules/system/decision_gate_schemas.py app/modules/system/api.py tests/test_v8_decision_gate_list_api.py`
- `git diff --check -- backend/app/modules/system/decision_gate_schemas.py backend/app/modules/system/api.py backend/tests/test_v8_decision_gate_list_api.py tasks/postdemo/v8/FPMS-V8-DECISION-GATE-LIST-API-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-LIST-API-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DECISION-GATE-LIST-API-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DECISION-GATE-LIST-API-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DECISION-GATE-LIST-API-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, Task 169 lines 473–485.
- Supplemental authority: row `28 / M4-G / H4-4` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; product work and evidence remain `NOT STARTED`.
- `chosen_runbook: P0-prereq-heavy-story` supersedes the historical runbook above for Delta-4 execution.
- This appendix is latest-wins only for the exact audit-list contract below; every other inherited byte and the exact Allowed Files list remain binding.

### Exact bodyless route, permission and response

- Add exactly `GET /api/v1/system/decision-gates`; its route signature and OpenAPI contract declare no request body, query parameter, path parameter, filter, page or as-of input.
- Enforce the existing parameter-injected `SystemParam.Read` permission and authentication dependencies. Success is HTTP 200, including an empty bare JSON list `[]`; missing/invalid authentication remains 401 and missing permission remains 403.
- Return one direct bare list of persisted audit-row DTOs, with no success/data wrapper, pagination envelope or effective-behavior result.
- Each item preserves persisted gate identity/code/value, source reference/version, scope, decision status, current identity, actor, effective/recorded time and supersedes identity verbatim. It adds no computed authority, fallback, precedence, currentness or effective-status field.

### Exact audit query, order and visibility

- Execute one explicit selected-column SELECT inside `transaction.no_autoflush`, ordered exactly by `recorded_at ASC, gate_id ASC`.
- Return all stored history: current, superseded, revoked and future-effective rows are equally visible. Do not filter by current identity, decision status, effective time or business scope.
- Perform zero writes and no clock read, add, flush, refresh, expire, commit, rollback or identity-map mutation.
- Do not call `resolve_decision_gate()`: the accepted read service resolves effective business behavior and cannot represent complete audit history.
- This bodyless audit route introduces no 400/404/409 business branch or authority-resolution error. Existing framework request-shape handling and authentication/permission errors remain unchanged; do not invent or remap errors.

### Dependencies and non-closure

- The accepted `FPMS-V8-DECISION-GATE-READ-SERVICE-20260712-01` remains a prerequisite contract, but this list route never delegates to its resolver. Preserve the inherited serialization after the confirm API and exclusive ownership of the allowlisted system API/schema files.
- Add no second endpoint, router rewire, persistence schema/model/migration, write service, authority inference, customer-decision activation, frontend or adjacent cleanup.

### Scoped TDD, evidence and gates

- RED through the public HTTP route must prove the missing exact path/method, bodyless signature, `SystemParam.Read`, bare-list shape, 200/401/403 behavior, complete visibility, stable order, one-SELECT/no-autoflush boundary and prohibition on resolver/write calls.
- GREEN is the smallest allowlisted API/schema/test implementation. Existing task-local pytest, scoped Ruff/format/diff, serialized SQLite verification, Evidence 1.1 initialization/finalization, independent review, repository task gate, atomic evidence validation and Done Definition remain binding for later High execution.
- This Ultra materialization performs no router/schema/product/test edit or evidence initialization and runs only the atomic task-file check.
