# DOCWIZ-CLOSE-01 — `#8` 向导 residual chain close audit

- Source: `docs/superpowers/plans/2026-04-03-docwiz-close-audit.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 根据 Step 1/2 representative slices 与 Step 3/4/5 residual contract 已完成证据，刷新 `#8 中间文件 5 步向导` 的 review baseline 与 mitigation ledger 状态。
- Exact closure slice:
  - 更新 `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - 更新 `docs/priority-ranked-mitigation-ledger.md`
  - 更新 `docs/superpowers/specs/2026-04-03-docwiz-close-audit-design.md`
  - 更新 `docs/superpowers/plans/2026-04-03-docwiz-close-audit.md`
- Explicit non-closure:
  - 不重审 `#13/#15/#19`
  - 不新增 residual story
  - 不做任何产品代码实现
- Remaining follow-up task ids:
  - `DOCWIZ-QA-CLOSE-01`
- Allowlist:
  - `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - `docs/priority-ranked-mitigation-ledger.md`
  - `docs/superpowers/specs/2026-04-03-docwiz-close-audit-design.md`
  - `docs/superpowers/plans/2026-04-03-docwiz-close-audit.md`
  - `tasks/postenhancement/backend/DOCWIZ-CLOSE-01.md`
  - `tasks/postenhancement/backend/DOCWIZ-QA-CLOSE-01.md`
- Verification:
  - `./scripts/task_validate.sh DOCWIZ-CLOSE-01`

## Execution Checklist

- [ ] Update `#8` to `Closed` in refresh review
- [ ] Remove `#8` from the non-closed mitigation ledger
- [ ] Update top-level counts consistently
- [ ] Keep `#13/#15/#19` unchanged
