# FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental integration prerequisite before grant catalog activation acceptance
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Make document impact preview consistent with Task37: canonical or executable-alias grant notices do
not report a generic `FEE_DRAFT` impact before client instruction, while confirmed official due
lineage remains visible. Preserve every non-grant fee-impact preview unchanged.

## Explicit Non-Closure

Do not change registration, actual FeeDraft creation/deletion, client-instruction workflow, grant
task creation/replacement, catalog/seed activation, frontend, schema, API, permission, or envelope.
Do not suppress non-grant fee impacts.

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01` (`PASS`)
- `FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01` (`PASS`)

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01`
- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_grant_preview_no_auto_draft.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/**`

No other file or artifact family is authorized. The shared document service requires exclusive
ownership during this task.

## Runtime Contracts

- Permission: existing `Doc.Create` preview permission.
- Status: confirmed grant preview 200; missing confirmation remains 409; no writes.
- Envelope: existing `DocumentImpactPreviewOut`.
- SQLite: every pytest invocation uses `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_preview_no_auto_draft.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_addgap_grant_preview_no_auto_draft.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_addgap_grant_preview_no_auto_draft.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_addgap_grant_preview_no_auto_draft.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_addgap_grant_preview_no_auto_draft.py tasks/additional_gaps/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/**`

## Supplemental Close Contract

This task is outside the frozen 47-entry manifest and must independently pass review/evidence/gate.
Task47 must record its closure before final release acceptance.

## Done Definition

Confirmed canonical and executable-alias grant previews retain official due lineage but contain no
generic fee impact; a non-grant fee template still reports its fee impact; RED/GREEN, Ruff/scope,
secret-safe evidence, independent review, atomic validation, and task gate pass. Only then may this
task be `PASS`.
