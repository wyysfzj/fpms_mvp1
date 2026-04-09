# EXPSTAT-CARRIER-SCHEMA-SPEC-01 — expense statistics carrier/schema authority batch freeze

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-carrier-authority.md`
- Type: `prerequisite`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 Module 4 剩余 `SPEC 5.10.2` residual 的 carrier/schema authority batch，明确 worker 与 department 必须分离进入 future prerequisite stories。
- Exact closure slice:
  - 新增 carrier authority spec/plan
  - 新增 future task graph
  - 生成 `artifacts/EXPSTAT-CARRIER-SCHEMA-SPEC-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不做 schema / migration
  - 不更新 final audit / close decision
- Remaining follow-up task ids:
  - `EXPSTAT-QA-CARRIER-SCHEMA-SPEC-01`
  - `EXPSTAT-WORKER-CARRIER-01`
  - `EXPSTAT-DEPARTMENT-CARRIER-01`
  - `EXPSTAT-CLOSE-02`
- Allowlist:
  - `docs/superpowers/specs/2026-04-09-expense-stat-carrier-authority-design.md`
  - `docs/superpowers/plans/2026-04-09-expense-stat-carrier-authority.md`
  - `tasks/postenhancement/backend/EXPSTAT-CARRIER-SCHEMA-SPEC-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-QA-CARRIER-SCHEMA-SPEC-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-WORKER-CARRIER-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-DEPARTMENT-CARRIER-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-CLOSE-02.md`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-CARRIER-SCHEMA-SPEC-01`

## Execution Checklist

- [ ] Freeze worker carrier as its own future schema-authority story
- [ ] Freeze department carrier as its own future schema-authority story
- [ ] Freeze future close-audit as a separate later story
