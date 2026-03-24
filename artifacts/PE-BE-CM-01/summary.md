# PE-BE-CM-01 Summary

- Scope: `/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/PE-BE-CM-01.md`
- Role: worker agent
- Status: PASS

## Implemented

- Added backend validation for case create/update to reject unknown `client_id` references before FK failure.
- Added priority completeness and duplicate-seq validation for case payloads.
- Tightened priority validation so blank `country_code` / `prio_no` values cannot bypass completeness checks.
- Added manual case status save rule requiring `app_no` and `filing_date` for non-`NOT_FILED` target statuses.
- Added document-driven status transition guard to block illegal regression from terminal case statuses.
- Extended `CaseStatus` enum with `ACCEPTED` and `GRANT_PENDING` to align status-effect template values.
- Added compatibility coverage for legacy `title` alias on full case update payloads.

## Scope Conclusion

- `FR-CM-05` is only partially covered in this task.
- Covered in current model: priority records (`0..n`) plus validation hardening.
- Blocked / not implemented by design in this task: 菌种保藏、PCT 国际/国家阶段专属字段、无效案专属字段。
- Rationale: current allowlist and existing ORM/schema do not contain storage fields or models for those attributes, and the task explicitly forbids schema / migration changes. Implementing them would require out-of-scope database/model expansion.

## Modified Files

- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/enums.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_case_fields.py`
- `backend/tests/test_b2_reply_chain.py`

## Validation

- `ruff check --fix ...` passed on allowlist files.
- `ruff format ...` passed on allowlist files.
- `ruff check ...` passed on allowlist files.
- `pytest -q tests/test_case_fields.py tests/test_b2_reply_chain.py` passed in `backend/` with `30 passed`.
- Repo-root `pytest -q backend/tests/test_case_fields.py backend/tests/test_b2_reply_chain.py` still fails due pre-existing Alembic relative-path resolution in `backend/tests/conftest.py`; not changed because outside task allowlist.
