# EXPSTAT-DEPARTMENT-PRE-01 — expense statistics department prerequisite freeze

- Source: `docs/superpowers/plans/2026-04-07-expense-stat-department-prereq.md`
- Type: `prerequisite`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 `SPEC 5.10.2` 中 department residual 的 truthful prerequisite authority，明确当前 schema 下哪些 department 语义不能伪实现。
- Exact closure slice:
  - 新增 department prerequisite spec/plan
  - 生成 `artifacts/EXPSTAT-DEPARTMENT-PRE-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不做 schema / migration
  - 不更新 final audit / close decision
  - 不吸收 worker residual
- Remaining follow-up task ids:
  - `EXPSTAT-QA-DEPARTMENT-PRE-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-07-expense-stat-department-prereq-design.md`
  - `docs/superpowers/plans/2026-04-07-expense-stat-department-prereq.md`
  - `tasks/postenhancement/backend/EXPSTAT-DEPARTMENT-PRE-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-QA-DEPARTMENT-PRE-01.md`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-DEPARTMENT-PRE-01`

## Execution Checklist

- [ ] Confirm current expense statistics path has no truthful department carrier
- [ ] Explicitly reject arbitrary grouping pseudo-closures
- [ ] Freeze that department statistics need a future carrier decision
