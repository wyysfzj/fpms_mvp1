# DOCWIZ-CLOSE-02 — `#8` 向导产品实现 close audit

- Source: `docs/superpowers/plans/2026-04-04-docwiz-product-close-audit.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 根据 Step 1/2 与 Step 3/4/5 的真实产品实现证据，刷新 `#8 中间文件 5 步向导` 的 review baseline 与 mitigation ledger 状态。
- Exact closure slice:
  - 更新 `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - 更新 `docs/priority-ranked-mitigation-ledger.md`
  - 更新 `docs/superpowers/specs/2026-04-04-docwiz-product-close-audit-design.md`
  - 更新 `docs/superpowers/plans/2026-04-04-docwiz-product-close-audit.md`
- Explicit non-closure:
  - 不重审 `#13/#15/#19`
  - 不新增 residual story
  - 不做任何产品代码实现
- Remaining follow-up task ids:
  - `DOCWIZ-QA-CLOSE-02`
- Allowlist:
  - `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - `docs/priority-ranked-mitigation-ledger.md`
  - `docs/superpowers/specs/2026-04-04-docwiz-product-close-audit-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-product-close-audit.md`
  - `tasks/postenhancement/backend/DOCWIZ-CLOSE-02.md`
  - `tasks/postenhancement/backend/DOCWIZ-QA-CLOSE-02.md`
- Verification:
  - `./scripts/task_validate.sh DOCWIZ-CLOSE-02`

## Execution Checklist

- [ ] Update `#8` to `Closed` in refresh review
- [ ] Remove `#8` from the non-closed mitigation ledger
- [ ] Update top-level counts consistently
- [ ] Keep `#13/#15/#19` unchanged
