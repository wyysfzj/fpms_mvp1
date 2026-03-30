# ANNRPT-BE-01 Evidence Summary

Task: extend `GET /annuity/tasks` with first-round annuity report filters and summary payload.

Scope completed:
- Added report response schema for the annuity task list.
- Extended `GET /annuity/tasks` to return `summary` while preserving the list contract.
- Supported grounded filters for `client_id`, `case_id`, `annuity_year`, `task_status`, and `date_range`.
- Kept `country` and `payment_status` minimal/no-op-compatible so the slice stays inside existing annuity task facts.

Verification:
- `python3 -m ruff check backend/app/modules/annuity/api.py backend/app/modules/annuity/service.py backend/app/modules/annuity/schemas.py backend/tests/test_annuity_report.py`
- `cd backend && PYTHONPATH=. pytest -q tests/test_annuity_report.py`
- `./scripts/task_validate.sh ANNRPT-BE-01`

Worktree note:
- Repository was already dirty outside the task allowlist at start, so baseline evidence is included alongside the task-scoped diff.
