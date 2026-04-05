# GF-CLOSE-02 — grant-fee product close audit refresh

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-product-close-audit.md`
- Type: `close audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 基于已提交的授权费产品实现，对 `#15` 做 strict close-audit，并在满足 `SPEC 2.0` §5.7.2–5.7.3 时将其从 `Partially Closed` 更新为 `Closed`。
- Exact closure slice:
  - 更新 `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - 更新 `docs/priority-ranked-mitigation-ledger.md`
  - 生成 `artifacts/GF-CLOSE-02/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不重审 `#19`
  - 不新开 residual implementation
- Remaining follow-up task ids:
  - `GF-QA-CLOSE-02`
- Allowlist:
  - `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - `docs/priority-ranked-mitigation-ledger.md`
  - `docs/superpowers/specs/2026-04-05-grant-fee-product-close-audit-design.md`
  - `docs/superpowers/plans/2026-04-05-grant-fee-product-close-audit.md`
  - `tasks/postenhancement/backend/GF-CLOSE-02.md`
  - `tasks/postenhancement/backend/GF-QA-CLOSE-02.md`
- Verification:
  - `./scripts/task_validate.sh GF-CLOSE-02`

## Execution Checklist

- [ ] Confirm `#15` committed product evidence closes §5.7.2 batch instruction + real notice generation
- [ ] Confirm `#15` committed product evidence closes §5.7.3 draft generation
- [ ] Update refresh review and mitigation ledger accordingly
