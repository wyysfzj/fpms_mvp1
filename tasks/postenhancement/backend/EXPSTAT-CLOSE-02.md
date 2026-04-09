# EXPSTAT-CLOSE-02 — future close audit for expense statistics carrier-backed residuals

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-carrier-authority.md`
- Type: `close-audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在 future worker/department carrier-backed 产品行为真实存在之后，刷新 Module 4 final-audit close decision。
- Exact closure slice:
  - 审计 worker/department residual 是否已有真实页面/API/用户路径
  - 若满足条件，才刷新 final audit / close rationale
- Explicit non-closure:
  - 不做产品实现
  - 不在 prerequisite-only 状态下提前 close
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - `docs/superpowers/specs/**`
  - `docs/superpowers/plans/**`
  - `tasks/postenhancement/backend/EXPSTAT-CLOSE-02.md`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-CLOSE-02`

## Execution Checklist

- [ ] Confirm carrier-backed worker behavior exists
- [ ] Confirm carrier-backed department behavior exists
- [ ] Reject premature closure if only prerequisite/spec waves exist
