# BE-A-APPLICANT-KIND-RULE-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Add backend service-layer validation that compares case `applicant_kind` against the first linked real `Applicant.applicant_type`.

This closure slice covers:

1. `POST /api/v1/cases`
2. `PUT /api/v1/cases/{case_id}` when the request can change `applicant_kind` or `applicants`
3. Preservation of the existing applicant-list error semantics

## Explicit Non-Closure

- Do not modify the `Applicant` data model or any migration.
- Do not implement TC-A-006 pytest automation beyond the focused backend rule tests.
- Do not implement TC-A-008 date/number rules.
- Do not modify frontend code or skeleton data.
- Do not infer applicant kind from names or seed-only metadata.
- Do not change existing applicant-list error codes or messages.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-APPLICANT-RULES-P0-02
- BE-A-DATE-NUMBER-RULES-01

## Allowed Files

- `tasks/backend/business_logic/BE-A-APPLICANT-KIND-RULE-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_case_applicant_kind_rule.py`
- `artifacts/BE-A-APPLICANT-KIND-RULE-01/**`

## Verification Commands

- `cd backend && python3 -m ruff check --fix app/modules/cases/service.py tests/test_case_applicant_kind_rule.py`
- `cd backend && python3 -m ruff format app/modules/cases/service.py tests/test_case_applicant_kind_rule.py`
- `cd backend && python3 -m ruff check app/modules/cases/service.py tests/test_case_applicant_kind_rule.py`
- `cd backend && pytest tests/test_case_applicant_kind_rule.py -q`
- `cd backend && pytest tests/test_case_type_combo_rule.py -q`
- `./scripts/evidence_run.sh BE-A-APPLICANT-KIND-RULE-01 task_gate ./scripts/task_validate.sh BE-A-APPLICANT-KIND-RULE-01`

## Evidence Path

- `artifacts/BE-A-APPLICANT-KIND-RULE-01/`
