# Summary

## Commands
- `python3 -m ruff check backend/app/modules/tasks/api.py backend/app/modules/tasks/schemas.py backend/app/modules/tasks/service.py backend/tests/test_task_special_search_api.py`
- `cd backend && PYTHONPATH=. pytest -q tests/test_task_special_search_api.py`
- `./scripts/task_validate.sh TASKSEARCH-BE-01`

## Results
- Ruff passed on the allowlisted task files.
- The task special-search pytest file passed.
- The task gate returned `Task Gate PASS`.

## Notes
- The special-search projection includes `remark` as a nullable field; the current `Task` ORM does not map a persisted task-level remark column, so the API emits `null` there.
