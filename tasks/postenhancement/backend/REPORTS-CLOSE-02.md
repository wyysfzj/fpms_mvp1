# REPORTS-CLOSE-02 — `#13` 报表产品实现 close audit

- Source: `docs/superpowers/plans/2026-04-05-reports-product-close-audit.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 根据当前 reports family ledger 与 `RPT-CASE / RPT-FEE / RPT-ANN` 的真实 residual product evidence，刷新 `#13 所有统计报表` 的 review baseline 与 mitigation ledger 状态。
- Exact closure slice:
  - 更新 `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - 更新 `docs/priority-ranked-mitigation-ledger.md`
  - 更新 `docs/superpowers/specs/2026-04-05-reports-product-close-audit-design.md`
  - 更新 `docs/superpowers/plans/2026-04-05-reports-product-close-audit.md`
- Explicit non-closure:
  - 不关闭 `#13`
  - 不重审 `#15/#19`
  - 不新增任何 residual story
  - 不做任何产品代码实现
- Remaining follow-up task ids:
  - `REPORTS-QA-CLOSE-02`
- Allowlist:
  - `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - `docs/priority-ranked-mitigation-ledger.md`
  - `docs/superpowers/specs/2026-04-05-reports-product-close-audit-design.md`
  - `docs/superpowers/plans/2026-04-05-reports-product-close-audit.md`
  - `tasks/postenhancement/backend/REPORTS-CLOSE-02.md`
  - `tasks/postenhancement/backend/REPORTS-QA-CLOSE-02.md`
- Verification:
  - `./scripts/task_validate.sh REPORTS-CLOSE-02`

## Execution Checklist

- [ ] Update `#13` to `Partially Closed` in refresh review
- [ ] Move `#13` into the mitigation ledger’s `Partially Closed` section
- [ ] Update top-level counts consistently
- [ ] Keep `#13` in the mitigation ledger with narrowed residual wording
- [ ] Keep `#15/#19` unchanged
