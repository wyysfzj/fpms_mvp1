# Department Master Router Refresh Plan

- date: `2026-04-09`
- design: `docs/superpowers/specs/2026-04-09-department-master-router-refresh-design.md`

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `medium`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Refresh

- insert `DEPTMASTER-ROUTER-01` between:
  - `DEPTMASTER-DB-01`
  - `DEPTMASTER-BE-01`

## Serialized Shared-file Decision

- `backend/app/api/router.py` is owned only by `DEPTMASTER-ROUTER-01`
- `DEPTMASTER-BE-01` may not touch router wiring

## Verification

- `./scripts/task_validate.sh DEPTMASTER-PROGRAM-REFRESH-01`
- `./scripts/task_validate.sh DEPTMASTER-QA-PROGRAM-REFRESH-01`
