# FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 46
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Enforce the single Task42 lineage-actionability invariant at every existing grant-fee mutation
entry point in the allowlisted service: direct draft generation (including reuse), batch client
instruction, and batch notice generation. `LEGACY_UNVERIFIED` and `SUPERSEDED` tasks must fail
closed with HTTP 409 semantics before any mutation or commit; `CONFIRMED` behavior remains unchanged.

## Explicit Non-Closure

Do not modify API routes, schemas, frontend behavior, replacement rules, lineage derivation,
workflow-state values, database schema, or legacy tests. Do not add a new endpoint or migration.

## Dependencies

- `FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01` (`PASS`)
- `FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01` (`PASS`)

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01`
- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_addgap_grant_mutation_lineage_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/**`

No other source, test, task, plan, manifest, or artifact family is authorized.

## Runtime Contracts

- Reuse Task41/42's single lineage derivation; no duplicate or weaker lineage semantics.
- Blocked direct and batch paths use `GRANT_FEE_TASK_LINEAGE_NOT_ACTIONABLE`, status 409, and
  identify the blocked task and lineage status. Batch validation completes before its mutation loop.
- Draft reuse must not bypass the lineage check and must not set `draft_generated` on a blocked task.
- Notice generation must check lineage before template rendering/document creation.
- Permission and response envelopes remain owned by existing API routes and are unchanged.
- SQLite: every pytest invocation uses `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_mutation_lineage_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py tests/test_addgap_grant_mutation_lineage_gate.py && .venv/bin/ruff format app/modules/grant_fees/service.py tests/test_addgap_grant_mutation_lineage_gate.py && .venv/bin/ruff check app/modules/grant_fees/service.py tests/test_addgap_grant_mutation_lineage_gate.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/service.py backend/tests/test_addgap_grant_mutation_lineage_gate.py tasks/additional_gaps/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/**`

## Supplemental Close Contract

This task is outside the frozen 47-entry manifest. It must independently pass review, evidence
validation, and its task gate before Task46 starts; Task47 must record it in the supplemental appendix.

## Done Definition

RED proves all three bypass families; the minimum shared service rule makes them GREEN; confirmed
normal paths remain covered; no blocked path mutates or commits; scoped Ruff/scope, independent
review, atomic validation, and task gate pass. Only then may this task be `PASS`.
