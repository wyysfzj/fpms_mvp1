# EXPSTAT-WORKER-PRE-01 — expense statistics worker prerequisite freeze

- Source: `docs/superpowers/plans/2026-04-07-expense-stat-worker-prereq.md`
- Type: `prerequisite`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 `SPEC 5.10.2` 中 worker residual 的 truthful prerequisite authority，明确当前 schema 下哪些 worker 语义不能伪实现。
- Exact closure slice:
  - 新增 worker prerequisite spec/plan
  - 生成 `artifacts/EXPSTAT-WORKER-PRE-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不做 schema / migration
  - 不更新 final audit / close decision
  - 不吸收 department residual
- Remaining follow-up task ids:
  - `EXPSTAT-QA-WORKER-PRE-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-07-expense-stat-worker-prereq-design.md`
  - `docs/superpowers/plans/2026-04-07-expense-stat-worker-prereq.md`
  - `tasks/postenhancement/backend/EXPSTAT-WORKER-PRE-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-QA-WORKER-PRE-01.md`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-WORKER-PRE-01`

## Execution Checklist

- [ ] Confirm current expense carrier has no truthful business worker field
- [ ] Explicitly reject `created_by / updated_by` pseudo-closure
- [ ] Freeze that worker statistics need a future carrier decision
