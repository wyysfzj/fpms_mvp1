# A-AUTO-PY-A-FOREIGN-REQUIRED-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only `TC-A-005` / `handle_tc_a_005` for A1 foreign-facing required fields:

- foreign flow missing `to_country` is rejected with stable business semantics
- foreign flow missing `foreign_agent_id` is rejected with stable business semantics
- non-agent client used as `foreign_agent_id` is rejected with stable business semantics
- legal agent client as `foreign_agent_id` succeeds

## Explicit Non-Closure

- Do not implement `TC-A-006`, `TC-A-007`, `TC-A-008`, or any other handler.
- Do not modify backend or frontend code.
- Do not modify skeleton data, YAML, JSON, schema, or Playwright assets.
- Do not expand ApiClient, DbAssert, or SeedCatalog.
- Do not change HANDLERS keys or testcase ids.
- Do not treat offline skip as real smoke PASS.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-APPLICANT-RULES-P0-01
- A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01
- BE-A-FOREIGN-REQUIRED-RULE-01 if real backend foreign-required semantics regress
- ENV-LOCAL-BACKEND-SMOKE-01 if local backend cannot run

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-FOREIGN-REQUIRED-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py`
- `artifacts/A-AUTO-PY-A-FOREIGN-REQUIRED-P0-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_foreign_required_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-005 -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_create_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_duplicate_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_invalid_combo_handler.py -q`
- `python3 -m ruff check --fix FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py`
- `python3 -m ruff format FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" FPMS_RUN_ID=LOCAL-RUN-AFOREIGN-001 FPMS_DB_DSN= pytest tests/test_wave_a.py -k TC-A-005 -q`
- `./scripts/task_validate.sh A-AUTO-PY-A-FOREIGN-REQUIRED-P0-01`

## Evidence Path

- `artifacts/A-AUTO-PY-A-FOREIGN-REQUIRED-P0-01/`
