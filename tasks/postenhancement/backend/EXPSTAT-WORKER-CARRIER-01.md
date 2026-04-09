# EXPSTAT-WORKER-CARRIER-01 — expense statistics worker carrier authority

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-carrier-authority.md`
- Type: `prerequisite`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 只冻结 `SPEC 5.10.2` worker residual 的 truthful business authority，并决定 future schema direction。
- Exact closure slice:
  - 决定 business worker ownership 应挂载的实体与字段
  - 冻结 migration/backfill direction
- Explicit non-closure:
  - 不处理 department authority
  - 不做产品实现
  - 不执行 migration
- Remaining follow-up task ids:
  - `EXPSTAT-CLOSE-02`
- Allowlist:
  - `docs/superpowers/specs/**`
  - `docs/superpowers/plans/**`
  - `tasks/postenhancement/backend/EXPSTAT-WORKER-CARRIER-01.md`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-WORKER-CARRIER-01`

## Execution Checklist

- [ ] Freeze business worker semantics without using `created_by / updated_by`
- [ ] Freeze worker carrier candidate and schema direction
- [ ] Freeze worker backfill direction or explicit null-first policy
