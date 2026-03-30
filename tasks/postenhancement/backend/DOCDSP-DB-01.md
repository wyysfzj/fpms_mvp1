# DOCDSP-DB-01 — documents dispatch 表与字段承载

- Source: `docs/superpowers/plans/2026-03-30-documents-dispatch-prereq.md`
- Type: `backend db prerequisite`
- Execution mode: Atomic

## Task Definition

- Goal: 为 `Document` 增加 `outgoing_reg_no / forward_date`，并新增 `DocDispatch / DocDispatchLine` 结构化承载。
- Exact closure slice:
  - `Document.outgoing_reg_no`
  - `Document.forward_date`
  - `DocDispatch`
  - `DocDispatchLine`
- Explicit non-closure:
  - 不改 dispatch action
  - 不改 envelope query
  - 不改前端
- Remaining follow-up task ids:
  - `DOCDSP-BE-MAIL-01`
  - `DOCDSP-BE-DISP-01`
  - `DOCDSP-BE-ENV-01`
  - `DOCDSP-FE-MAIL-01`
  - `DOCDSP-FE-DISP-01`
  - `DOCDSP-FE-ENV-01`
  - `DOCDSP-QA-01`
