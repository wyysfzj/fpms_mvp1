# BE-A-CASE-COMBO-RULE-TEST-MAINT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: low

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Update `backend/tests/test_case_type_combo_rule.py` so the case type combo regression tests include a valid minimal applicant prerequisite and can reach the intended `CASE_TYPE_COMBO_INVALID` and duplicate `case_no` semantics under the now-enforced applicant list rule.

This closure slice only covers the stale test prerequisite update.

## Explicit Non-Closure

- Do not modify `backend/app/modules/cases/service.py`.
- Do not modify the `Applicant` model or seed scripts.
- Do not change production backend/frontend/pytest automation.
- Do not alter the expected `CASE_TYPE_COMBO_INVALID` or `CASE_NO_DUPLICATE` semantics.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/backend/test_maintenance/BE-A-CASE-COMBO-RULE-TEST-MAINT-01.md`
- `backend/tests/test_case_type_combo_rule.py`
- `artifacts/BE-A-CASE-COMBO-RULE-TEST-MAINT-01/**`

## Verification Commands

- `cd backend && python3 -m ruff check --fix tests/test_case_type_combo_rule.py`
- `cd backend && python3 -m ruff format tests/test_case_type_combo_rule.py`
- `cd backend && python3 -m ruff check tests/test_case_type_combo_rule.py`
- `cd backend && pytest tests/test_case_type_combo_rule.py -q`
- `./scripts/evidence_run.sh BE-A-CASE-COMBO-RULE-TEST-MAINT-01 task_gate ./scripts/task_validate.sh BE-A-CASE-COMBO-RULE-TEST-MAINT-01`

## Evidence Path

- `artifacts/BE-A-CASE-COMBO-RULE-TEST-MAINT-01/`
