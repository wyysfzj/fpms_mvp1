# Expense Stat Carrier Authority Plan

- date: `2026-04-09`
- design: `docs/superpowers/specs/2026-04-09-expense-stat-carrier-authority-design.md`

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `no immediate implementation lane`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-prereq-heavy-story`

## Result Shape

- `schema-authority prerequisite planning only`
- no product implementation in this wave

## Batch Manifest

### Wave 1

- `EXPSTAT-CARRIER-SCHEMA-SPEC-01`
  - owner: `main thread`
  - exact closure slice:
    - freeze worker/department carrier authority batch
    - create future task graph
  - explicit non-closure:
    - no product code
    - no schema/migration
    - no final-audit update

### Wave 2

- `EXPSTAT-QA-CARRIER-SCHEMA-SPEC-01`
  - owner: `main thread`
  - exact closure slice:
    - audit planning wave evidence and gate status
  - explicit non-closure:
    - no product code
    - no planning rewrite

## Future Task Graph

### `EXPSTAT-WORKER-CARRIER-01`

- exact closure slice:
  - freeze truthful business worker authority and resulting schema direction
- explicit non-closure:
  - no department authority
  - no product implementation
  - no migration execution in the same task

### `EXPSTAT-DEPARTMENT-CARRIER-01`

- exact closure slice:
  - freeze truthful business department authority and resulting schema direction
- explicit non-closure:
  - no worker authority
  - no product implementation
  - no migration execution in the same task

### `EXPSTAT-CLOSE-02`

- exact closure slice:
  - refresh final audit only after truthful carrier-backed product behavior exists
- explicit non-closure:
  - no implementation
  - no premature close decision

## Serialized Shared-file Decisions

- current planning wave only touches doc/task files
- future worker and department stories must remain serialized by policy even if they both
  later touch `backend/app/modules/expenses/models.py`
- `EXPSTAT-CLOSE-02` must not run before future carrier-backed implementation evidence exists

## Verification

- `./scripts/task_validate.sh EXPSTAT-CARRIER-SCHEMA-SPEC-01`
- `./scripts/task_validate.sh EXPSTAT-QA-CARRIER-SCHEMA-SPEC-01`
