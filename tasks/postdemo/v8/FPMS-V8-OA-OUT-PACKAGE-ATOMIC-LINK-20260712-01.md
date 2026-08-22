# FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `67`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `453`
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

Existing OA_OUT entrypoint calls `prepare_oa_reply()` so OA_OUT creation and its unique package reply link succeed or roll back together; task remains open and no seam logic is duplicated.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `Task10:FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_ensure_service.py.
- `inherited` — `Task11:FPMS-ADDGAP-OA-RESOLVE-API-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-RESOLVE-API-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-RESOLVE-API-20260710-01/summary.md, artifacts/FPMS-ADDGAP-OA-RESOLVE-API-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-RESOLVE-API-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_resolve_api.py.
- `inherited` — `Task12:FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-oa-page-resolve.spec.ts.
- `inherited` — `Task13:FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01/summary.md, artifacts/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_out_keeps_task_open.py, backend/tests/test_b2_reply_chain.py, backend/tests/test_spec_alignment_e2e.py.
- `inherited` — `Task70:FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_document_ui_deadline_generation.py.

- Approved source dependency cell (verbatim): prepare-OA-reply seam; Tasks10–13/70

### Shared ownership serialization

- `backend/app/modules/documents/service.py` order key `5`; project this order only across owners present in the active manifest.
- `backend/app/modules/official_workflows/service.py` order key `6`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01.md`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_oa_out_package_atomic_link.py`
- `artifacts/FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_oa_out_package_atomic_link.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_oa_out_package_atomic_link.py tests/test_addgap_oa_ensure_service.py tests/test_addgap_oa_resolve_api.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py tests/test_document_ui_deadline_generation.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-oa-page-resolve.spec.ts --workers=1`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/official_workflows/service.py tests/test_v8_oa_out_package_atomic_link.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/official_workflows/service.py tests/test_v8_oa_out_package_atomic_link.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/official_workflows/service.py tests/test_v8_oa_out_package_atomic_link.py`
- `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/official_workflows/service.py backend/tests/test_v8_oa_out_package_atomic_link.py tasks/postdemo/v8/FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OA-OUT-PACKAGE-ATOMIC-LINK-20260712-01` pass. Only then may this task be reported PASS.
