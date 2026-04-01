# CASEFILTER-PRE-01 Evidence Summary

- Exact closure completed: added `applicant_id` to the case applicant write payload, persisted it in the full create/update write path for `T_CaseApplicant`, validated the masterdata applicant before write, and normalized blank/whitespace `applicant_id` to `None`.
- Explicit non-closure respected: no `/cases` query enhancement, no frontend changes, no `patent_no`, no `fee_status`, no detail response changes, and no limited update changes.
- Verification:
  - Red test: `cd backend && PYTHONPATH=. pytest -q tests/test_case_applicant_masterdata_link_write_path.py::test_blank_applicant_id_normalizes_to_none_on_create_and_update` failed before normalization was restored.
  - Lint: `python3 -m ruff check backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_applicant_masterdata_link_write_path.py` passed.
  - Green test: `cd backend && PYTHONPATH=. pytest -q tests/test_case_applicant_masterdata_link_write_path.py` passed with 5 tests green.
  - Task gate: `./scripts/task_validate.sh CASEFILTER-PRE-01` passed after the evidence bundle was written.
- Stability follow-up:
  - The masterdata applicant seed in `test_create_case_persists_case_applicant_applicant_id` was made unique to avoid full-suite collisions against `Applicant.name_cn` unique constraint.
  - Targeted verification was rerun after that test-data fix and remained green.
- Dirty baseline: the repository already contained unrelated modified/untracked files outside the allowlist, so the evidence bundle includes a baseline external-file list.
