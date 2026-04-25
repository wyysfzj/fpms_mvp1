# BE-A-CASE-COMBO-RULE-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Add the minimal backend service-layer validation for illegal CaseType + PatentCategory combinations so `TC-A-004` has a real product rule and stable API error semantics to assert later.

This task only covers the real backend rule. It does not implement the skeleton pytest handler.

## Explicit Non-Closure

- Do not implement `TC-A-004` pytest automation.
- Do not remove `handle_tc_a_004` from skeleton status.
- Do not modify skeleton YAML, JSON, manifests, or testcase IDs.
- Do not modify frontend or Playwright.
- Do not add database schema, migration, or system config tables.
- Do not use duplicate case number, invalid enum, or missing-field validation as a substitute for illegal-combination validation.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-CASE-INVALID-COMBO-P1-02

## Allowed Files

- `tasks/backend/business_logic/BE-A-CASE-COMBO-RULE-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_case_type_combo_rule.py`
- `artifacts/BE-A-CASE-COMBO-RULE-01/**`

## Verification Commands

- `python3 -m ruff check --fix backend/app/modules/cases/service.py backend/tests/test_case_type_combo_rule.py`
- `python3 -m ruff format backend/app/modules/cases/service.py backend/tests/test_case_type_combo_rule.py`
- `python3 -m ruff check backend/app/modules/cases/service.py backend/tests/test_case_type_combo_rule.py`
- `pytest backend/tests/test_case_type_combo_rule.py -q`
- `pytest backend/tests/test_consulting_e2e.py -q`
- `pytest backend/tests/test_case_fields.py -q`
- `./scripts/task_validate.sh BE-A-CASE-COMBO-RULE-01`

## Evidence Path

- `artifacts/BE-A-CASE-COMBO-RULE-01/`
