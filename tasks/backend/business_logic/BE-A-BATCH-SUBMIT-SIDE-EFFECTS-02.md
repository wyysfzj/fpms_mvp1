# BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement the minimal backend side-effect contract for `POST /api/v1/cases/batch-filing/submit`:

- preserve existing batch filing status transition and error semantics
- wire `CaseBatchFilingActionIn.generate_list` from API to service
- when `generate_list=true`, register stable submission-list `Document` records for updated cases
- after successful batch filing, create idempotent open `APPLY_FEE_LIMIT` tasks for updated cases
- extend the response with backward-compatible `document_ids` and `created_task_ids`

## Explicit Non-Closure

- Do not implement `handle_tc_a_011`
- Do not modify `FPMS_Automation_Skeleton_Pack/pytest_python/**`
- Do not modify skeleton YAML / JSON / manifest / schema / Playwright
- Do not modify frontend UI
- Do not implement full `TC-A-013` deadline/reminder automation
- Do not implement fee draft, pay list, bill, payment, or commission logic
- Do not add document/task storage abstractions or unrelated endpoints

## Remaining Follow-Up Task IDs

- `A-AUTO-PY-A-BATCH-SUBMIT-P0-01`
- `A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01`
- `BE-A-BATCH-SUBMIT-SIDE-EFFECTS-03` if side-effect implementation requires files outside this allowlist

## Allowed Files

- `tasks/backend/business_logic/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02.md`
- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/tests/test_case_batch_filing_side_effects.py`
- `artifacts/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02/**`

Conditionally allowed only for directly related response-schema expectation maintenance:

- `backend/tests/test_case_batch_filing_action.py`

## Verification Commands

Run from `backend/` unless noted:

- `pytest tests/test_case_batch_filing_side_effects.py -q`
- `python3 -m ruff check --fix app/modules/cases/api.py app/modules/cases/service.py app/modules/cases/schemas.py tests/test_case_batch_filing_side_effects.py`
- `python3 -m ruff format app/modules/cases/api.py app/modules/cases/service.py app/modules/cases/schemas.py tests/test_case_batch_filing_side_effects.py`
- `python3 -m ruff check app/modules/cases/api.py app/modules/cases/service.py app/modules/cases/schemas.py tests/test_case_batch_filing_side_effects.py`
- `pytest tests/test_case_batch_filing_side_effects.py -q`
- `pytest tests/test_case_batch_filing_action.py -q`
- `pytest tests/test_case_batch_filing_query.py -q`
- `pytest tests/test_case_type_combo_rule.py -q`
- `pytest tests/test_case_date_number_rules.py -q`
- `pytest tests/test_case_applicant_kind_rule.py -q`
- `./scripts/task_validate.sh BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02`

## Evidence Path

- `artifacts/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02/results.jsonl`
- `artifacts/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02/summary.md`
- `artifacts/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02/git/diff.patch`
- `artifacts/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02/baseline_allowlist.diff`
- `artifacts/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02/baseline_external_files.txt`
