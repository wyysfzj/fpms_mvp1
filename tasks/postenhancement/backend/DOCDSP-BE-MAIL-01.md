# DOCDSP-BE-MAIL-01 — 邮寄信息登记 action

- Source: `docs/superpowers/plans/2026-03-30-documents-dispatch-prereq.md`
- Type: `backend action`
- Execution mode: Atomic

## Task Definition

- Goal: 为现有去文提供批量登记 `OutgoingRegNo / ForwardDate` 的 action。
- Exact closure slice:
  - 批量邮寄登记 request/response contract
  - 批量更新 `Document.outgoing_reg_no / forward_date`
- Explicit non-closure:
  - 不生成交接单
  - 不做 envelope print query
  - 不改前端
- Remaining follow-up task ids:
  - `DOCDSP-BE-DISP-01`
  - `DOCDSP-BE-ENV-01`
  - `DOCDSP-FE-MAIL-01`
  - `DOCDSP-FE-DISP-01`
  - `DOCDSP-FE-ENV-01`
  - `DOCDSP-QA-01`
