# FRCOM03-BE-CASE-01 Summary

Implemented the case contract slice for current effective agent split configuration.

## Closure slice completed

- `GET /cases/{id}` now returns `agent_splits` for the current effective configuration, or `[]` when unset.
- `PUT /cases/{id}` now persists `agent_splits` with minimal validation:
  - agent_id values must be unique
  - each share ratio must be greater than `0` and at most `100`
  - share ratios must sum to `100`
  - split members must be internal users with role code `Agent`
  - an empty split list is allowed

## Verification

- `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_agent_split_api.py`
- `cd backend && pytest -q tests/test_case_agent_split_api.py`
- `./scripts/task_validate.sh FRCOM03-BE-CASE-01`

All three checks passed, including the task gate.

## Notes

- Baseline evidence recorded one pre-existing external dirty file outside the task allowlist: `backend/app/modules/cases/models.py`.
- `baseline_allowlist.diff` is intentionally empty because there was no pre-existing allowlist diff at task start.
- The regression bundle includes the per-row ratio validation case that rejects `150/-50`-style payloads.
- The task test file uses its own SQLite test harness so it does not depend on the repo-wide Alembic fixture that currently has multiple heads.
- No commission generation, settlement, report, or frontend behavior was changed.
