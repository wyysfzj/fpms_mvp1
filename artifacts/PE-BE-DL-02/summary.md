# PE-BE-DL-02

Status: PASS

Scope:
- `backend/app/modules/tasks/api.py`
- `backend/app/modules/tasks/service.py`
- `backend/app/modules/tasks/schemas.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_task_template.py`

Changes:
- added Batch 2 manual-task delete support in the tasks API/service
- added regression coverage for deleting a manually maintained task
- fixed the delete endpoint to obey FastAPI 204 no-body semantics required by AGENTS

Validation:
- `ruff check backend/app/modules/tasks/api.py backend/app/modules/tasks/service.py backend/app/modules/tasks/schemas.py backend/app/modules/tasks/task_generation_service.py backend/app/modules/documents/service.py backend/app/modules/annuity/service.py backend/tests/test_task_template.py`
- `cd backend && pytest -q tests/test_task_template.py`
- `./scripts/task_validate.sh PE-BE-DL-02`

Notes:
- this closes a Batch 2 manual-maintenance slice, not all remaining Tasks backend scope
- current allowlist diff also overlaps prior worktree changes in `backend/app/modules/documents/service.py`; monitor should treat that as contamination risk, not as newly claimed task behavior
