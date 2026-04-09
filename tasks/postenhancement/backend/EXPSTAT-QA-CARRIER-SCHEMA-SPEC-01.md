# EXPSTAT-QA-CARRIER-SCHEMA-SPEC-01 — QA audit for expense carrier/schema authority planning

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-carrier-authority.md`
- Type: `qa-audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `EXPSTAT-CARRIER-SCHEMA-SPEC-01` planning wave 的 evidence、gate 和 follow-up graph 是否完整。
- Exact closure slice:
  - 审计 planning/spec wave evidence
  - 生成 `artifacts/EXPSTAT-QA-CARRIER-SCHEMA-SPEC-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不做第二轮 planning rewrite
- Remaining follow-up task ids:
  - `EXPSTAT-WORKER-CARRIER-01`
  - `EXPSTAT-DEPARTMENT-CARRIER-01`
  - `EXPSTAT-CLOSE-02`
- Allowlist:
  - `tasks/postenhancement/backend/EXPSTAT-QA-CARRIER-SCHEMA-SPEC-01.md`
  - `artifacts/EXPSTAT-CARRIER-SCHEMA-SPEC-01/**`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-QA-CARRIER-SCHEMA-SPEC-01`

## Execution Checklist

- [ ] Verify worker and department remain separate future stories
- [ ] Verify no product implementation is claimed
- [ ] Verify future close-audit remains blocked on carrier-backed behavior
