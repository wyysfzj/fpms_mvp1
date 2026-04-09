# EXPSTAT-DEPARTMENT-CARRIER-01 — expense statistics department carrier authority

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-carrier-authority.md`
- Type: `prerequisite`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 只冻结 `SPEC 5.10.2` department residual 的 truthful business authority，并决定 future schema direction。
- Exact closure slice:
  - 决定 business department ownership 应挂载的实体与字段
  - 冻结 migration/backfill direction
- Explicit non-closure:
  - 不处理 worker authority
  - 不做产品实现
  - 不执行 migration
- Remaining follow-up task ids:
  - `EXPSTAT-CLOSE-02`
- Allowlist:
  - `docs/superpowers/specs/**`
  - `docs/superpowers/plans/**`
  - `tasks/postenhancement/backend/EXPSTAT-DEPARTMENT-CARRIER-01.md`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-DEPARTMENT-CARRIER-01`

## Execution Checklist

- [ ] Freeze business department semantics without using client/case pseudo-carriers
- [ ] Freeze department carrier candidate and schema direction
- [ ] Freeze department backfill direction or explicit null-first policy
