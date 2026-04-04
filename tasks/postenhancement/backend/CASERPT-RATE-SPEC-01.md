# CASERPT-RATE-SPEC-01 — `RPT-CASE` grant-rate semantics freeze

- Source: `docs/superpowers/plans/2026-04-04-case-report-grant-rate.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 `RPT-CASE` 中 `授权率` 的分子/分母语义，明确哪些案件状态计入授权成功、哪些状态计入分母、哪些状态必须排除，并判断该指标是否能在当前 carrier 下直接进入实现。
- Exact closure slice:
  - 更新 `docs/superpowers/specs/2026-04-04-case-report-grant-rate-design.md`
  - 更新 `docs/superpowers/plans/2026-04-04-case-report-grant-rate.md`
- Explicit non-closure:
  - 不做任何案件统计产品实现补丁
  - 不做年/月趋势统计
  - 不触发 `#13` 或 `RPT-CASE` close update
- Remaining follow-up task ids:
  - `CASERPT-QA-RATE-SPEC-01`
  - `CASERPT-RATE-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-04-case-report-grant-rate-design.md`
  - `docs/superpowers/plans/2026-04-04-case-report-grant-rate.md`
  - `tasks/postenhancement/backend/CASERPT-RATE-SPEC-01.md`
  - `tasks/postenhancement/backend/CASERPT-QA-RATE-SPEC-01.md`
- Verification:
  - `./scripts/task_validate.sh CASERPT-RATE-SPEC-01`

## Execution Checklist

- [ ] Freeze grant-rate numerator semantics
- [ ] Freeze denominator set and excluded in-progress statuses
- [ ] Record implementation-readiness judgment
- [ ] Keep all product work deferred
