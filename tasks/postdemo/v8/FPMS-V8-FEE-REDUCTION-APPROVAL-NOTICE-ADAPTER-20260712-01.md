# FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `127`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `569`
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

Freeze resolver semantic `FEE_REDUCTION_APPROVAL_NOTICE`; a reviewed confirmed notice records/reuses scoped approval evidence, while reference-only/unknown notices do nothing. It does not activate the catalog row, create an obligation/draft or change lifecycle state.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FEE-REDUCTION-APPROVAL-RECORD-SERVICE-20260712-01`
- `FPMS-V8-APPLICATION-FEE-NOTICE-OBLIGATION-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `Task18:FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01/summary.md, artifacts/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_oa_subsequent_task_identity.py.
- `inherited` — `Task19:FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_catalog_classification.py.
- `inherited` — `Task20:FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01/summary.md, artifacts/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-notice-catalog-ui-clarity.spec.ts.
- `inherited` — `Task21:FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_catalog_reference_gate.py.
- `inherited` — `Task33:FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_oa_acceptance_activation.py.
- `inherited` — `Task38:FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_grant_activation.py.

- Approved source dependency cell (verbatim): approval service; notice catalog/seed predecessor PASS; serialized after application-fee notice obligation

### Shared ownership serialization

- `backend/app/modules/documents/fee_linking_service.py` order key `2`; project this order only across owners present in the active manifest.
- `backend/app/modules/documents/semantics.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01.md`
- `backend/app/modules/documents/semantics.py`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/tests/test_v8_fee_reduction_approval_notice_adapter.py`
- `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_notice_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_fee_reduction_approval_notice_adapter.py tests/test_addgap_oa_subsequent_task_identity.py tests/test_addgap_notice_catalog_classification.py tests/test_addgap_notice_catalog_reference_gate.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_addgap_notice_grant_activation.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-notice-catalog-ui-clarity.spec.ts --workers=1`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_fee_reduction_approval_notice_adapter.py && .venv/bin/ruff format app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_fee_reduction_approval_notice_adapter.py && .venv/bin/ruff check app/modules/documents/semantics.py app/modules/documents/fee_linking_service.py tests/test_v8_fee_reduction_approval_notice_adapter.py`
- `git diff --check -- backend/app/modules/documents/semantics.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_v8_fee_reduction_approval_notice_adapter.py tasks/postdemo/v8/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-FEE-REDUCTION-APPROVAL-NOTICE-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.
