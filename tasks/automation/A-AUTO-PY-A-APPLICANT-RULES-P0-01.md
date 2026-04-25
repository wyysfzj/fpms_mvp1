# A-AUTO-PY-A-APPLICANT-RULES-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only `TC-A-006` / `handle_tc_a_006` for A1 applicant list rules if the real backend supports the complete closure:

- no applicants is rejected
- multiple first applicants is rejected
- applicant kind mismatch with first applicant is rejected or has stable backend warning/confirm semantics
- corrected applicant kind succeeds

## Explicit Non-Closure

- Do not implement `TC-A-008`.
- Do not implement any other A or W0 handler.
- Do not modify backend or frontend code.
- Do not modify skeleton data, YAML, JSON, schema, or Playwright assets.
- Do not remove skeleton markers for partial coverage.
- Do not fake applicant-kind mismatch behavior in pytest.

## Remaining Follow-Up Task IDs

- BE-A-APPLICANT-RULES-01 if applicant kind mismatch needs backend enforcement.
- A-AUTO-PY-A-APPLICANT-RULES-P0-02 if backend/product rules are added and automation can resume.
- BE-A-DATE-NUMBER-RULES-01 for likely `TC-A-008` rule gaps.
- ENV-LOCAL-BACKEND-SMOKE-01 if later real smoke is blocked by local backend.

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-APPLICANT-RULES-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py`
- `artifacts/A-AUTO-PY-A-APPLICANT-RULES-P0-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_foreign_required_handler.py -q`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py`
- If backend rule exists and handler is implemented:
  - `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_applicant_rules_handler.py -q`
  - `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-006 -q`
  - real smoke with `FPMS_DB_DSN=` and fresh `FPMS_RUN_ID`

## Evidence Path

- `artifacts/A-AUTO-PY-A-APPLICANT-RULES-P0-01/`
