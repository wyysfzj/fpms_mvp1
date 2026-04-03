# COMMSPLIT-CLOSE-01 — review baseline close audit

- Source: `docs/superpowers/plans/2026-04-03-commission-split-close-audit.md`
- Type: `doc change`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 基于已完成的 COMMSPLIT backend/frontend/evidence 链，更新 `#5 多代理人提成分成` 的 review baseline 和 mitigation ledger，纠正旧的 `Still Missing` 结论。
- Exact closure slice:
  - 更新 `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - 更新 `docs/priority-ranked-mitigation-ledger.md`
- Explicit non-closure:
  - 不修改任何产品代码
  - 不重审 `#8/#13/#15/#19`
  - 不新增新的 planning decomposition
- Remaining follow-up task ids:
  - `COMMSPLIT-QA-10`
- Allowlist:
  - `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - `docs/priority-ranked-mitigation-ledger.md`
  - `tasks/postenhancement/backend/COMMSPLIT-CLOSE-01.md`
  - `tasks/postenhancement/backend/COMMSPLIT-QA-10.md`
- Verification:
  - `./scripts/task_validate.sh COMMSPLIT-CLOSE-01`

## Execution Checklist

- [ ] Confirm only `#5` is reclassified
- [ ] Update summary counts consistently
- [ ] Update priority queue consistently
- [ ] Preserve explicit residual non-closed items for other review entries
- [ ] Generate required artifacts and dirty-baseline notes
