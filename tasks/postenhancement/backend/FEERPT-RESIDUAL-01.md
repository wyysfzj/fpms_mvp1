# FEERPT-RESIDUAL-01 — `RPT-FEE` residual capability map

- Source: `docs/superpowers/plans/2026-04-04-fee-report-residual.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 对 `RPT-FEE` 形成一份 strict residual capability map，明确当前 first-round fee statistics report 已闭合了什么、相对 `FPMS SPEC 2.0` `9.4.2` 还剩哪些 grouped dimensions / source semantics / metrics，并推荐一个最小 residual implementation slice。
- Exact closure slice:
  - 更新 `docs/superpowers/specs/2026-04-04-fee-report-residual-design.md`
  - 更新 `docs/superpowers/plans/2026-04-04-fee-report-residual.md`
- Explicit non-closure:
  - 不做任何费用统计产品实现补丁
  - 不重做 `FEERPT-BE-01` / `FEERPT-FE-01`
  - 不触发 `#13` close update
- Remaining follow-up task ids:
  - `FEERPT-QA-RESIDUAL-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-04-fee-report-residual-design.md`
  - `docs/superpowers/plans/2026-04-04-fee-report-residual.md`
  - `tasks/postenhancement/backend/FEERPT-RESIDUAL-01.md`
  - `tasks/postenhancement/backend/FEERPT-QA-RESIDUAL-01.md`
- Verification:
  - `./scripts/task_validate.sh FEERPT-RESIDUAL-01`

## Execution Checklist

- [ ] Separate first-round implemented closure from full-spec residuals
- [ ] Freeze residual grouped dimensions / source semantics / metric buckets
- [ ] Recommend one next residual implementation slice
- [ ] Keep all product work deferred
