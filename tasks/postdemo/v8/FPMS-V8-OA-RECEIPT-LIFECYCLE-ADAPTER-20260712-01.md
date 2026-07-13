# FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `70`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `456`
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

Existing receipt transaction also calls `OA_RECEIPT_ARCHIVED`, preserving exactly-one task close and legacy SUB_EXAM.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-OA-RECEIPT-ARCHIVED-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `Task14:FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_receipt_same_case_gate.py.
- `inherited` — `Task15:FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_receipt_source_gate.py.
- `inherited` — `Task16:FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/summary.md, artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_receipt_history_scan.py.
- `inherited` — `Task17:FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01/summary.md, artifacts/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_receipt_archive_event.py.
- `inherited` — `Task56:FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_out_keeps_task_open.py, backend/tests/test_b2_reply_chain.py.
- `inherited` — `Task70:FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_document_ui_deadline_generation.py.

- Approved source dependency cell (verbatim): OA receipt rule; Tasks14–17/56/70

### Shared ownership serialization

- `backend/app/modules/official_workflows/service.py` order key `9`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_v8_oa_receipt_lifecycle_adapter.py`
- `artifacts/FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_oa_receipt_lifecycle_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_oa_receipt_lifecycle_adapter.py tests/test_addgap_receipt_same_case_gate.py tests/test_addgap_oa_receipt_source_gate.py tests/test_addgap_receipt_history_scan.py tests/test_addgap_oa_receipt_archive_event.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_document_ui_deadline_generation.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_v8_oa_receipt_lifecycle_adapter.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_v8_oa_receipt_lifecycle_adapter.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_v8_oa_receipt_lifecycle_adapter.py`
- `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_v8_oa_receipt_lifecycle_adapter.py tasks/postdemo/v8/FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-OA-RECEIPT-LIFECYCLE-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
