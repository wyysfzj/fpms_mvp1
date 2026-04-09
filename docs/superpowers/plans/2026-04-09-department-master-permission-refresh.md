# Department Master Permission Refresh Plan

- date: `2026-04-09`
- design: `docs/superpowers/specs/2026-04-09-department-master-permission-refresh-design.md`

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `medium`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Refresh

- insert `DEPTMASTER-PERM-01` between:
  - `DEPTMASTER-ROUTER-01`
  - `DEPTMASTER-BE-01`

## Serialized Shared-file Decision

- `backend/app/modules/rbac/service.py` is owned only by `DEPTMASTER-PERM-01`
- `DEPTMASTER-BE-01` may not touch permission seed

