# DOCDSP-FE-MAIL-01 — 邮寄信息登记页面能力

- Source: `docs/superpowers/plans/2026-03-30-documents-dispatch-prereq.md`
- Type: `frontend workflow page`
- Execution mode: Atomic

## Task Definition

- Goal: 在 dispatch 流程页上提供筛选、勾选和批量邮寄登记能力。
- Exact closure slice:
  - dispatch 流程页筛选与列表
  - 文档勾选
  - `OutgoingRegNo / ForwardDate` 批量登记
- Explicit non-closure:
  - 不做交接单详情
  - 不做信封打印预览
  - 不改 `DocumentList.vue`
- Remaining follow-up task ids:
  - `DOCDSP-FE-DISP-01`
  - `DOCDSP-FE-ENV-01`
  - `DOCDSP-QA-01`
