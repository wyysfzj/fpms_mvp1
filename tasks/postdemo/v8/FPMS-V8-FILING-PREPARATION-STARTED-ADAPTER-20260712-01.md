# FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `59`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `445`
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

Resolving/creating the filing preparation package records `FILING_PREPARATION_STARTED` exactly once.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `Task05:FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/summary.md, artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_workpkg_resolve_key_schema.py.
- `inherited` — `Task06:FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_filing_ensure_service.py.
- `inherited` — `Task07:FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/summary.md, artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_filing_resolve_api.py.
- `inherited` — `Task08:FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-page-resolve.spec.ts.
- `inherited` — `Task09:FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/summary.md, artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-case-entry.spec.ts.

- Approved source dependency cell (verbatim): preparation rule; Tasks05–09 regressions

### Shared ownership serialization

- `backend/app/modules/official_workflows/service.py` order key `1`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01.md`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_filing_preparation_started_adapter.py`
- `artifacts/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_filing_preparation_started_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_filing_preparation_started_adapter.py tests/test_addgap_workpkg_resolve_key_schema.py tests/test_addgap_filing_ensure_service.py tests/test_addgap_filing_resolve_api.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-page-resolve.spec.ts src/tests/addgap-filing-case-entry.spec.ts --workers=1`
- `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_filing_preparation_started_adapter.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_filing_preparation_started_adapter.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_filing_preparation_started_adapter.py`
- `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_filing_preparation_started_adapter.py tasks/postdemo/v8/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FILING-PREPARATION-STARTED-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
