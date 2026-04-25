# BATCH-A-BATCH1-RULES-IMPLEMENTATION-01

## Batch ID

- Batch ID: BATCH-A-BATCH1-RULES-IMPLEMENTATION-01
- Role: lead / worker coordinator
- chosen_runbook: P0-prereq-heavy-story

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

## Goal

Implement the Batch 1 rule stack required to unblock TC-A-006 and TC-A-008 automation:

1. Add real Applicant applicant_type data support.
2. Add backend applicant kind mismatch validation.
3. Add backend date/status/app number validation.
4. Implement TC-A-006 pytest automation.
5. Implement TC-A-008 pytest automation.

## Shared File Serialization

- `backend/app/modules/cases/service.py` is shared by backend rule tasks and must be edited serially.
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py` is shared by automation tasks and must be edited serially.
- SQLite write tests must not run concurrently.
- No worker may own more than one atomic task file.

## Wave Order

### Wave 0: Read-Only Discovery

- Freeze migration path, applicant API shape, case rule helper location, and stale skeleton-state assertion files.
- No product code edits.

### Wave 1

- Task: BE-A-APPLICANT-DATA-MODEL-01
- Task file: `tasks/backend/data_model/BE-A-APPLICANT-DATA-MODEL-01.md`
- Dependency: product contract only.

### Wave 2

- Task: BE-A-APPLICANT-KIND-RULE-01
- Task file: `tasks/backend/business_logic/BE-A-APPLICANT-KIND-RULE-01.md`
- Dependency: BE-A-APPLICANT-DATA-MODEL-01 PASS.
- Must not run concurrently with BE-A-DATE-NUMBER-RULES-01 if both edit `backend/app/modules/cases/service.py`.

### Wave 3

- Task: BE-A-DATE-NUMBER-RULES-01
- Task file: `tasks/backend/business_logic/BE-A-DATE-NUMBER-RULES-01.md`
- Dependency: product contract and serialized ownership of `backend/app/modules/cases/service.py`.

### Wave 4

- Task: A-AUTO-PY-A-APPLICANT-RULES-P0-02
- Task file: `tasks/automation/A-AUTO-PY-A-APPLICANT-RULES-P0-02.md`
- Dependencies:
  - BE-A-APPLICANT-DATA-MODEL-01 PASS
  - BE-A-APPLICANT-KIND-RULE-01 PASS

### Wave 5

- Task: A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01
- Task file: `tasks/automation/A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01.md`
- Dependencies:
  - BE-A-DATE-NUMBER-RULES-01 PASS
  - serialized ownership of `wave_a.py`

## Per-Task Closure Slices

### BE-A-APPLICANT-DATA-MODEL-01

Add persisted Applicant `applicant_type` backend data support, schema/API exposure, dev seed support, and targeted tests. Do not implement case applicant kind validation.

Allowed files:

- `tasks/backend/data_model/BE-A-APPLICANT-DATA-MODEL-01.md`
- `backend/app/modules/masterdata/applicants/models.py`
- `backend/app/modules/masterdata/applicants/schemas.py`
- `backend/app/modules/masterdata/applicants/api.py`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_applicant_data_model.py`
- `backend/tests/test_applicant_masterdata_api.py`
- `backend/tests/test_masterdata_prereq_schema.py`
- `backend/tests/test_masterdata_prereq_contract.py`
- `backend/alembic/versions/**`
- `artifacts/BE-A-APPLICANT-DATA-MODEL-01/**`

Verification:

- scoped ruff for allowed backend files
- `cd backend && pytest tests/test_applicant_data_model.py -q`
- `cd backend && pytest tests/test_applicant_masterdata_api.py tests/test_masterdata_prereq_schema.py tests/test_masterdata_prereq_contract.py -q`
- migration sanity if a migration is added
- task gate

### BE-A-APPLICANT-KIND-RULE-01

Add backend service-layer `CASE_APPLICANT_KIND_MISMATCH` validation based on real Applicant `applicant_type`. Preserve existing applicant list errors.

Allowed files:

- `tasks/backend/business_logic/BE-A-APPLICANT-KIND-RULE-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_case_applicant_kind_rule.py`
- `artifacts/BE-A-APPLICANT-KIND-RULE-01/**`

Verification:

- scoped ruff for allowed backend files
- `cd backend && pytest tests/test_case_applicant_kind_rule.py -q`
- `cd backend && pytest tests/test_case_type_combo_rule.py -q`
- task gate

### BE-A-DATE-NUMBER-RULES-01

Add backend TC-A-008 service rules and stable errors: `CASE_PUBLISHED_FIELDS_REQUIRED`, `CASE_GRANTED_FIELDS_REQUIRED`, `CASE_FILING_BEFORE_PRIORITY`, and `CASE_APP_NO_INVALID`.

Allowed files:

- `tasks/backend/business_logic/BE-A-DATE-NUMBER-RULES-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_case_date_number_rules.py`
- `artifacts/BE-A-DATE-NUMBER-RULES-01/**`

Verification:

- scoped ruff for allowed backend files
- `cd backend && pytest tests/test_case_date_number_rules.py -q`
- `cd backend && pytest tests/test_case_type_combo_rule.py -q`
- task gate

### A-AUTO-PY-A-APPLICANT-RULES-P0-02

Implement TC-A-006 pytest automation. Assert no applicants, duplicate first applicant, applicant kind mismatch, and corrected applicant kind success.

Allowed files:

- `tasks/automation/A-AUTO-PY-A-APPLICANT-RULES-P0-02.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `artifacts/A-AUTO-PY-A-APPLICANT-RULES-P0-02/**`

Verification:

- targeted pytest handler tests
- targeted `test_wave_a.py -k TC-A-006`
- real smoke with fresh `FPMS_RUN_ID` and `FPMS_DB_DSN=`
- task gate

### A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01

Implement TC-A-008 pytest automation. Assert published/granted missing fields, filing date before priority, filing date equal priority accepted, and invalid app number.

Allowed files:

- `tasks/automation/A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_date_number_rules_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `artifacts/A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01/**`

Verification:

- targeted pytest handler tests
- targeted `test_wave_a.py -k TC-A-008`
- real smoke with fresh `FPMS_RUN_ID` and `FPMS_DB_DSN=`
- task gate

## Explicit Non-Closure

- Do not implement more than one atomic task inside one worker.
- Do not concurrently edit shared ownership files.
- Do not fake backend business semantics in pytest handlers.
- Do not use skeleton-only data to infer production Applicant type.
- Do not modify skeleton YAML/JSON/schema/Playwright unless an atomic task explicitly allows it.

## Evidence

- Batch evidence: `artifacts/BATCH-A-BATCH1-RULES-IMPLEMENTATION-01/**`
- Per-task evidence: `artifacts/<TASK-ID>/**`

## Follow-Up Task IDs

- `PRODUCT-A-APPLICANT-TYPE-MODEL-CONFIRM-01` if data model contract is insufficient.
- `BE-A-APPLICANT-KIND-RULE-FIX-01` if mismatch validation needs correction.
- `BE-A-DATE-NUMBER-RULES-FIX-01` if TC-A-008 backend rule implementation is incomplete.
- `A-AUTO-PY-A-APPLICANT-RULES-P0-03-FIX` if automation envelope mismatches backend.
- `A-AUTO-PY-A-DATE-NUMBER-RULES-P0-02-FIX` if automation envelope mismatches backend.
- `ENV-LOCAL-BACKEND-SMOKE-01` if real smoke environment is unavailable.
