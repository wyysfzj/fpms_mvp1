# EXPSTAT-SCHEMA-PROGRAM-SPEC-01 — expense statistics schema program freeze

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-schema-program.md`
- Type: `prerequisite`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 Module 4 剩余 gap 的 staged schema/carrier implementation program，明确 worker lane 先行、department lane 先补 master prerequisite。
- Exact closure slice:
  - 新增 schema-program spec/plan
  - 生成 `artifacts/EXPSTAT-SCHEMA-PROGRAM-SPEC-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不执行 migration
  - 不更新 final audit / close decision
- Remaining follow-up task ids:
  - `EXPSTAT-QA-SCHEMA-PROGRAM-SPEC-01`
  - `EXPSTAT-WORKER-DB-01`
  - `EXPSTAT-WORKER-BE-01`
  - `EXPSTAT-WORKER-FE-01`
  - `EXPSTAT-WORKER-QA-01`
  - `EXPSTAT-DEPARTMENT-MASTER-PRE-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-09-expense-stat-schema-program-design.md`
  - `docs/superpowers/plans/2026-04-09-expense-stat-schema-program.md`
  - `tasks/postenhancement/backend/EXPSTAT-SCHEMA-PROGRAM-SPEC-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-QA-SCHEMA-PROGRAM-SPEC-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-WORKER-DB-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-WORKER-BE-01.md`
  - `tasks/postenhancement/frontend/EXPSTAT-WORKER-FE-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-WORKER-QA-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-DEPARTMENT-MASTER-PRE-01.md`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-SCHEMA-PROGRAM-SPEC-01`
