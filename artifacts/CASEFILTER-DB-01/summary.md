# CASEFILTER-DB-01 Evidence Summary

- Exact closure slice completed: add nullable `T_CaseApplicant.applicant_id` carrier plus SQLite-safe migration and index/reference for a stable applicant masterdata query path.
- Non-closure respected: no case create/update payload wiring, no `/cases` query enhancement, no frontend, no `patent_no`, no `fee_status`.
- Verification:
  - `python3 -m ruff check backend/app/modules/cases/models.py backend/alembic/versions/casefilter_pre_01_case_applicant_masterdata_link.py backend/tests/test_case_applicant_masterdata_link_schema.py` -> pass
  - `pytest -q backend/tests/test_case_applicant_masterdata_link_schema.py` -> pass
  - `cd backend && DATABASE_URL=sqlite:////tmp/fpms_casefilter_pre_verify_$$.db alembic upgrade head` -> pass
  - `./scripts/task_validate.sh CASEFILTER-DB-01` -> pass after evidence bundle was written
- Dirty baseline: repository started with unrelated modified/untracked files outside this task allowlist; captured in `baseline_external_files.txt`.
