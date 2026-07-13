# FPMS-V8-LC-CONTRACTS-20260712-01

Status: READY / NOT STARTED
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
