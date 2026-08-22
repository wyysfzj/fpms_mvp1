# FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `124`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `561`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

GovPayment registration links payment evidence and appends one payment activity.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-PAYMENT-EVIDENCE-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): payment evidence; serialized

### Shared ownership serialization

- `backend/app/modules/annuity/service.py` order key `5`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01.md`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_gov_payment_activity_adapter.py`
- `artifacts/FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Reuse deep-module activity identity; the existing financial action must not append a duplicate activity.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_gov_payment_activity_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_gov_payment_activity_adapter.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_gov_payment_activity_adapter.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_gov_payment_activity_adapter.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_gov_payment_activity_adapter.py`
- `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_gov_payment_activity_adapter.py tasks/postdemo/v8/FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GOV-PAYMENT-FEE-ACTIVITY-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
