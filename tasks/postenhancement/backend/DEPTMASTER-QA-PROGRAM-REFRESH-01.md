# DEPTMASTER-QA-PROGRAM-REFRESH-01 — audit router refresh wave

- Source: `docs/superpowers/plans/2026-04-09-department-master-router-refresh.md`
- Type: `qa-audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `DEPTMASTER-PROGRAM-REFRESH-01` evidence 和 gate，确认 router ownership 已 truthfully 插回 batch graph。
- Exact closure slice:
  - audit router refresh evidence
  - generate `artifacts/DEPTMASTER-QA-PROGRAM-REFRESH-01/**`
- Explicit non-closure:
  - 不做 router wiring
  - 不做 backend CRUD
- Remaining follow-up task ids:
  - `DEPTMASTER-ROUTER-01`
  - `DEPTMASTER-BE-01`
- Allowlist:
  - task/docs/artifacts only
- Verification:
  - `./scripts/task_validate.sh DEPTMASTER-QA-PROGRAM-REFRESH-01`
