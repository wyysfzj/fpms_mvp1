# FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 28 acceptance
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the three obsolete executable-OA impact-preview fixtures in the two allowlisted test files with
the approved Task24/Task27/Task28 contract: preview and source-document creation supply a confirmed
explicit official due date. Preserve semantic state-effect, read-only preview, reply-source status,
and all unrelated assertions unchanged.

## Explicit Non-Closure

Do not modify product, seed, migration, schema, service, API, manifest, specification, plan, or any
other test. Do not delete coverage, weaken fail-closed behavior, change grant behavior, or absorb
Task28 implementation/acceptance or Task47 final-close work.

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01` (`PASS`)
- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01` (`PASS`)
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01` implementation at `REVIEW`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01` acceptance
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_addgap_document_semantic_state_effect.py`
- `backend/tests/test_document_impact_preview_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

No other source, test, task, manifest, specification, plan, shared ownership file, or artifact family
is authorized.

## Runtime Contracts

- Permission/status/envelope: unchanged; test-fixture alignment only.
- SQLite: serialize every pytest invocation through `/tmp/fpms_addgap_sqlite_test.lock`.
- Simplified Chinese UI: N/A.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_semantic_state_effect.py tests/test_document_impact_preview_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_addgap_document_semantic_state_effect.py tests/test_document_impact_preview_api.py && .venv/bin/ruff format tests/test_addgap_document_semantic_state_effect.py tests/test_document_impact_preview_api.py && .venv/bin/ruff check tests/test_addgap_document_semantic_state_effect.py tests/test_document_impact_preview_api.py`
- Scope: `git diff --check -- backend/tests/test_addgap_document_semantic_state_effect.py backend/tests/test_document_impact_preview_api.py tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Execution and Close-Audit Contract

This task is supplemental to the frozen 47-entry manifest and must not modify its spec/plan. It must
pass its own independent review, evidence validation, and task gate before Task28 acceptance; Task47
must record its ID/evidence/gate/closure decision.

## Done Definition

The exact two-file target passes while preserving all non-deadline assertions; scoped Ruff/scope,
credential-safe RED/GREEN evidence, independent review, atomic validation, and task gate pass; exact
closure and non-closure are respected. Only then may this supplemental task be `PASS`.
