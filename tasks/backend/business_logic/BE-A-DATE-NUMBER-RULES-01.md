# BE-A-DATE-NUMBER-RULES-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Add backend service-layer date/status/app number rules for TC-A-008.

This closure slice covers:

1. `POST /api/v1/cases`
2. `PUT /api/v1/cases/{case_id}` when the request can change `status`, `app_no`, `filing_date`, `pub_date`, `pub_no`, `grant_date`, `grant_no`, `first_annuity_year`, or `valid_until`
3. Stable business errors for published/granted status validation, priority date comparison, and app number normalization

Required semantics:

- `PUBLISHED` requires `app_no`, `filing_date`, `pub_no`, `pub_date`
- `GRANTED` requires `app_no`, `filing_date`, `pub_no`, `pub_date`, `grant_no`, `grant_date`, `first_annuity_year`, `valid_until`
- If priorities exist, `filing_date` must be greater than or equal to the earliest `prio_date`
- `app_no` must be trimmed before validation, must reject empty or whitespace-only values when required, and must reject control-character values
- Keep schema-level length limits unchanged
- Do not add a strict jurisdiction-specific regex

Stable error codes:

- `CASE_PUBLISHED_FIELDS_REQUIRED`
- `CASE_GRANTED_FIELDS_REQUIRED`
- `CASE_FILING_BEFORE_PRIORITY`
- `CASE_APP_NO_INVALID`

## Explicit Non-Closure

- Do not implement pytest automation handlers beyond the focused backend tests in this task.
- Do not modify frontend code.
- Do not modify skeleton testcase data.
- Do not modify the `Applicant` model or applicant kind rule behavior.
- Do not add schema or migration changes.
- Do not absorb TC-A-006 applicant-kind behavior into this task.

## Remaining Follow-Up Task IDs

- `A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01`

## Allowed Files

- `tasks/backend/business_logic/BE-A-DATE-NUMBER-RULES-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_case_date_number_rules.py`
- `artifacts/BE-A-DATE-NUMBER-RULES-01/**`

## Verification Commands

- `cd backend && python3 -m ruff check --fix app/modules/cases/service.py tests/test_case_date_number_rules.py`
- `cd backend && python3 -m ruff format app/modules/cases/service.py tests/test_case_date_number_rules.py`
- `cd backend && python3 -m ruff check app/modules/cases/service.py tests/test_case_date_number_rules.py`
- `cd backend && pytest tests/test_case_date_number_rules.py -q`
- `cd backend && pytest tests/test_case_type_combo_rule.py -q`
- `./scripts/evidence_run.sh BE-A-DATE-NUMBER-RULES-01 task_gate ./scripts/task_validate.sh BE-A-DATE-NUMBER-RULES-01`

## Evidence Path

- `artifacts/BE-A-DATE-NUMBER-RULES-01/`
