# EXPSTAT-CLOSE-01 — expense statistics close-audit wording refresh

- Source: `docs/superpowers/plans/2026-04-07-expense-stat-close-audit.md`
- Type: `close audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 基于已提交 prerequisite/result-ledger 证据，刷新 final audit 对 Module 4 剩余 gap 的描述，明确它已进入 carrier-blocked state。
- Exact closure slice:
  - 更新 `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - 生成 `artifacts/EXPSTAT-CLOSE-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不把 Module 4 改成 `Closed`
  - 不更新 refresh review
- Remaining follow-up task ids:
  - `EXPSTAT-QA-CLOSE-01`
- Allowlist:
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-07-expense-stat-close-audit-design.md`
  - `docs/superpowers/plans/2026-04-07-expense-stat-close-audit.md`
  - `tasks/postenhancement/backend/EXPSTAT-CLOSE-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-QA-CLOSE-01.md`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-CLOSE-01`
