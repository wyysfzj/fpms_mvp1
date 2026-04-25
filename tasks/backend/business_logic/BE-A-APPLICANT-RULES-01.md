# BE-A-APPLICANT-RULES-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Add real backend service-layer validation for case `applicant_kind` mismatch with the first applicant type, if the real applicant data model exposes a safe applicant type source field.

## Explicit Non-Closure

- Do not implement `handle_tc_a_006`.
- Do not modify `FPMS_Automation_Skeleton_Pack/pytest_python/**`.
- Do not modify skeleton YAML, JSON, manifest, schema, or Playwright assets.
- Do not modify frontend UI.
- Do not add database schema or Alembic migrations.
- Do not implement `TC-A-008` date/number rules.
- Do not change existing applicant-list error semantics.

## Remaining Follow-Up Task IDs

- PRODUCT-A-APPLICANT-KIND-RULE-CONFIRM-01
- BE-A-APPLICANT-DATA-MODEL-01 if applicant type must be added to the real model
- BE-A-DATE-NUMBER-RULES-01 for `TC-A-008` forward blocker

## Allowed Files

- `tasks/backend/business_logic/BE-A-APPLICANT-RULES-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_case_applicant_rules.py`
- `artifacts/BE-A-APPLICANT-RULES-01/**`

## Verification Commands

- `python3 -m ruff check backend/app/modules/cases/service.py`
- `cd backend && pytest tests/test_case_type_combo_rule.py -q`

## Evidence Path

- `artifacts/BE-A-APPLICANT-RULES-01/`
