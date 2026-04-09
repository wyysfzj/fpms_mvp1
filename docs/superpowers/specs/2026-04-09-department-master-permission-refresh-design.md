# Department Master Permission Refresh Design

- date: `2026-04-09`

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `medium`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem

`DEPTMASTER-BE-01` needs truthful permission enforcement, but current RBAC seed does not provide `Department.Read` / `Department.Write`. Without a dedicated permission slice, backend endpoints would be unreachable for seeded users.

## Refresh Decision

- add new atomic task `DEPTMASTER-PERM-01`
- serialize ownership:
  - `DEPTMASTER-PERM-01` before `DEPTMASTER-BE-01`

## Non-closure

- no backend CRUD implementation
- no frontend path
