# FEOVERVIEW-CLOSE-01 — fee overview product close audit refresh

- Source: `docs/superpowers/plans/2026-04-06-fee-overview-close-audit.md`
- Type: `close audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 基于已提交的费用情况查询产品实现，对 `#16` 与 `SPEC 2.0` §5.11 做 strict close-audit，并在满足双表查询 first-round parity 时刷新 review / final-audit 结论。
- Exact closure slice:
  - 更新 `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - 更新 `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - 生成 `artifacts/FEOVERVIEW-CLOSE-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不更新 `priority-ranked-mitigation-ledger.md`
  - 不重审 `SPEC 5.10.2`
- Remaining follow-up task ids:
  - `FEOVERVIEW-QA-CLOSE-01`
- Allowlist:
  - `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-06-fee-overview-close-audit-design.md`
  - `docs/superpowers/plans/2026-04-06-fee-overview-close-audit.md`
  - `tasks/postenhancement/backend/FEOVERVIEW-CLOSE-01.md`
  - `tasks/postenhancement/backend/FEOVERVIEW-QA-CLOSE-01.md`
- Verification:
  - `./scripts/task_validate.sh FEOVERVIEW-CLOSE-01`

## Execution Checklist

- [ ] Confirm committed product evidence closes `SPEC 2.0` §5.11 upper pane with truthful `T_GovPayment` authority
- [ ] Confirm committed product evidence closes `SPEC 2.0` §5.11 lower pane with truthful `T_CaseReceipt` authority
- [ ] Confirm committed product evidence closes first-round upper-pane `fee_type` semantics
- [ ] Update refresh review and final audit ledger accordingly
