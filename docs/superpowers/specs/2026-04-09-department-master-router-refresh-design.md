# Department Master Router Refresh Design

- date: `2026-04-09`
- target: `DEPTMASTER program refresh`

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `medium`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem

`DEPTMASTER-BE-01` was planned without first-entry router ownership. Because `backend/app/api/router.py` does not yet include a department router, the department master module cannot become reachable without a dedicated serialized router slice.

## Refresh Decision

- add new atomic task `DEPTMASTER-ROUTER-01`
- keep router wiring separate from `DEPTMASTER-BE-01`
- serialize ownership:
  - `DEPTMASTER-ROUTER-01` before `DEPTMASTER-BE-01`

## Non-closure

- no backend CRUD implementation
- no frontend path
- no expense department stats
