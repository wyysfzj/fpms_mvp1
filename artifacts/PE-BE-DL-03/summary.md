# PE-BE-DL-03

Status: PASS

Scope:
- `backend/app/modules/tasks/api.py`
- `backend/app/modules/tasks/service.py`
- `backend/app/modules/tasks/schemas.py`
- `backend/tests/test_task_template.py`

Changes:
- added current-user scoped role views on `/tasks?as=worker|supervisor`
- enriched `/tasks/today` output with `case_no`, `client_name`, timestamps
- expanded backend regression coverage for role-filtered list and today reminders

Validation:
- `cd backend && pytest -q tests/test_task_template.py -k 'today_returns_enriched_fields_and_role_filtered or current_user_role_view'`
- `cd backend && pytest -q tests/test_task_template.py`

Notes:
- no schema change
- no Batch 3 scope touched
