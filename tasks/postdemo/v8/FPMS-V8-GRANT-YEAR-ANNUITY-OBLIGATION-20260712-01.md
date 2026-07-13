# FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01

Status: READY / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `130`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `572`
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

Registration notice creates only listed grant-year annuity lines, year, amount and due; no fixed combined fee code.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-RECOGNIZE-OBLIGATION-20260712-01`

### External, gate and inherited prerequisites

- `inherited` — `Task35:FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_lineage_schema.py.
- `inherited` — `Task36:FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_source_deadline.py.
- `inherited` — `Task37:FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_auto_draft_gate.py.
- `inherited` — `Task38:FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_grant_activation.py.
- `inherited` — `Task39:FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_replacement_service.py.
- `inherited` — `Task40:FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_replacement_api.py.
- `inherited` — `Task41:FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_list_lineage_projection.py.
- `inherited` — `Task42:FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_state_lineage_gate.py.
- `inherited` — `Task43:FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-lineage-ui.spec.ts.
- `inherited` — `Task44:FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-replacement-ui.spec.ts.
- `inherited` — `Task49:FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_b3_fee_linking.py.
- `inherited` — `Task50:FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_notice_task_creation.py.
- `inherited` — `Task52:FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_preview_no_auto_draft.py.
- `inherited` — `Task53:FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_spec_alignment_e2e.py.
- `inherited` — `Task55:FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_notice_oa_acceptance_activation.py.
- `inherited` — `Task57:FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_worklist_api.py.
- `inherited` — `Task58:FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_state_machine_api.py.
- `inherited` — `Task59:FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/git/diff.patch; targeted tests backend/tests/test_addgap_grant_mutation_lineage_gate.py.
- `inherited` — `Task60:FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/git/diff.patch; targeted tests FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts.
- `inherited` — `Task61:FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_draft_linkage_api.py.
- `inherited` — `Task62:FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/summary.md, artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/git/diff.patch; targeted tests backend/tests/test_grant_fee_notice_document_api.py.
- `inherited` — `Task64:FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02.md; PASS evidence artifacts/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02/summary.md, artifacts/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02/results.jsonl, artifacts/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02/git/diff.patch; targeted tests backend/tests/test_addgap_document_create_atomicity.py.
- `inherited` — `Task69:FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02`: Accepted task file tasks/additional_gaps/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02.md; PASS evidence artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/summary.md, artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/results.jsonl, artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/git/diff.patch; targeted tests backend/tests/test_grant_fee_prereq_schema.py.

- Approved source dependency cell (verbatim): recognize; grant lineage regressions

### Shared ownership serialization

- `backend/app/modules/grant_fees/service.py` order key `3`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md`
- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_v8_grant_year_annuity_obligation.py`
- `artifacts/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_year_annuity_obligation.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_grant_year_annuity_obligation.py tests/test_addgap_grant_lineage_schema.py tests/test_addgap_grant_source_deadline.py tests/test_addgap_grant_auto_draft_gate.py tests/test_addgap_notice_grant_activation.py tests/test_addgap_grant_replacement_service.py tests/test_addgap_grant_replacement_api.py tests/test_addgap_grant_list_lineage_projection.py tests/test_addgap_grant_state_lineage_gate.py tests/test_b3_fee_linking.py tests/test_grant_fee_notice_task_creation.py tests/test_addgap_grant_preview_no_auto_draft.py tests/test_spec_alignment_e2e.py tests/test_addgap_notice_oa_acceptance_activation.py tests/test_grant_fee_worklist_api.py tests/test_grant_fee_state_machine_api.py tests/test_addgap_grant_mutation_lineage_gate.py tests/test_grant_fee_draft_linkage_api.py tests/test_grant_fee_notice_document_api.py tests/test_addgap_document_create_atomicity.py tests/test_grant_fee_prereq_schema.py`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-lineage-ui.spec.ts src/tests/addgap-grant-replacement-ui.spec.ts src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts --workers=1`
- `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py tests/test_v8_grant_year_annuity_obligation.py && .venv/bin/ruff format app/modules/grant_fees/service.py tests/test_v8_grant_year_annuity_obligation.py && .venv/bin/ruff check app/modules/grant_fees/service.py tests/test_v8_grant_year_annuity_obligation.py`
- `git diff --check -- backend/app/modules/grant_fees/service.py backend/tests/test_v8_grant_year_annuity_obligation.py tasks/postdemo/v8/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01` pass. Only then may this task be reported PASS.
