# FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `13. Wave 5 — PayList internal/official/payment boundary`
Catalog ordinal: `162`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `625`
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

PayList detail returns internal artifacts, official workbook gate/status and payment facts separately.

## Explicit Non-Closure

No endpoint/UI/schema and no adjacent service rule or second dataset beyond the row's observable behavior. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-PAYLIST-PAYMENT-EXPORT-DECOUPLE-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): decouple

### Shared ownership serialization

- `backend/app/modules/annuity/service.py` order key `9`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01.md`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_pay_list_export_artifact_read.py`
- `artifacts/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_pay_list_export_artifact_read.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_pay_list_export_artifact_read.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_pay_list_export_artifact_read.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_pay_list_export_artifact_read.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_pay_list_export_artifact_read.py`
- `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_pay_list_export_artifact_read.py tasks/postdemo/v8/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PAYLIST-EXPORT-ARTIFACT-READ-20260712-01` pass. Only then may this task be reported PASS.
