# DEPTMASTER-QA-PERM-REFRESH-01 — audit permission refresh wave

- Source: `docs/superpowers/plans/2026-04-09-department-master-permission-refresh.md`
- Type: `qa-audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `DEPTMASTER-PERM-REFRESH-01` evidence 和 gate。
- Exact closure slice:
  - audit permission refresh evidence
  - generate `artifacts/DEPTMASTER-QA-PERM-REFRESH-01/**`
- Explicit non-closure:
  - 不做 permission seed implementation
  - 不做 backend CRUD
- Remaining follow-up task ids:
  - `DEPTMASTER-PERM-01`
  - `DEPTMASTER-BE-01`
- Allowlist:
  - task/docs/artifacts only
- Verification:
  - `./scripts/task_validate.sh DEPTMASTER-QA-PERM-REFRESH-01`
