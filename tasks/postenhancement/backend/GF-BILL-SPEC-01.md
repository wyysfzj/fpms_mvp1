# GF-BILL-SPEC-01 — 授权费 bill linkage 语义冻结

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-bill-linkage.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 `#15` 中 grant-fee bill linkage 的 authority、`GrantFeeTask -> FeeDraft -> Bill` 最小回投语义，以及第一条最小 bill-linkage follow-up story。
- Exact closure slice:
  - 更新 `docs/superpowers/specs/2026-04-05-grant-fee-bill-linkage-design.md`
  - 更新 `docs/superpowers/plans/2026-04-05-grant-fee-bill-linkage.md`
- Explicit non-closure:
  - 不做任何产品实现补丁
  - 不扩展 grant-fee 状态机
  - 不做 receipt/payment semantics
  - 不更新 `#15` close decision
- Remaining follow-up task ids:
  - `GF-QA-BILL-SPEC-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-05-grant-fee-bill-linkage-design.md`
  - `docs/superpowers/plans/2026-04-05-grant-fee-bill-linkage.md`
  - `tasks/postenhancement/backend/GF-BILL-SPEC-01.md`
  - `tasks/postenhancement/backend/GF-QA-BILL-SPEC-01.md`
- Verification:
  - `./scripts/task_validate.sh GF-BILL-SPEC-01`

## Execution Checklist

- [ ] Freeze bill-linkage source-of-truth
- [ ] Freeze task-state non-expansion boundary
- [ ] Recommend one first bill-linkage follow-up story
- [ ] Keep receipt/payment/document residuals deferred
