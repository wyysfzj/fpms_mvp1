# FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `126`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `568`
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

Freeze resolver semantic `APPLICATION_FEE_NOTICE`; a reviewed confirmed notice with exact due/source/item lines creates/reuses the application-fee obligation, while preview difference enters review. For a PCT case it applies exemptions only from confirmed RO/search/report evidence through the pure PCT policy, never from `case_type` alone. It does not activate the catalog row or create a draft.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`
- `FPMS-V8-PCT-FEE-POLICY-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `Task22:FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_document_deadline_carrier.py.
- `inherited` — `Task23:FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_document_deadline_read_projection.py.
- `inherited` — `Task24:FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_document_deadline_create_api.py.
- `inherited` — `Task25:FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_document_deadline_update_api.py.
- `inherited` — `Task26:FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01/summary.md, artifacts/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_legacy_deadline_task_sync.py.
- `inherited` — `Task27:FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01/summary.md, artifacts/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_deadline_fail_closed.py.
- `inherited` — `Task28:FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_document_deadline_impact_preview.py.
- `inherited` — `Task29:FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_document_wizard_deadline_backend.py.

- Approved source dependency cell (verbatim): recognize, `FPMS-V8-PCT-FEE-POLICY`; Tasks22–29

### Shared ownership serialization

- `backend/app/modules/documents/fee_linking_service.py` order key `1`; project this order only across owners present in the active manifest.
- `backend/app/modules/documents/semantics.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01.md`
- `backend/app/modules/documents/semantics.py`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/tests/test_v8_application_fee_notice_obligation.py`
- `artifacts/FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_application_fee_notice_obligation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_application_fee_notice_obligation.py tests/test_addgap_document_deadline_carrier.py tests/test_addgap_document_deadline_read_projection.py tests/test_addgap_document_deadline_create_api.py tests/test_addgap_document_deadline_update_api.py tests/test_addgap_legacy_deadline_task_sync.py tests/test_addgap_oa_deadline_fail_closed.py tests/test_addgap_document_deadline_impact_preview.py tests/test_addgap_document_wizard_deadline_backend.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_application_fee_notice_obligation.py && .venv/bin/ruff format app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_application_fee_notice_obligation.py && .venv/bin/ruff check app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_application_fee_notice_obligation.py`
- `git diff --check -- backend/app/modules/documents/semantics.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_application_fee_notice_obligation.py tasks/postdemo/v8/FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01` pass. Only then may this task be reported PASS.
