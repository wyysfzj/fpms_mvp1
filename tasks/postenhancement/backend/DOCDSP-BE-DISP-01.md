# DOCDSP-BE-DISP-01 — 文件交接单生成与详情

- Source: `docs/superpowers/plans/2026-03-30-documents-dispatch-prereq.md`
- Type: `backend action/query`
- Execution mode: Atomic

## Task Definition

- Goal: 提供交接单生成 action 与详情查看 query。
- Exact closure slice:
  - `T_DocDispatch / T_DocDispatchLine` 生成
  - 交接单详情读取
- Explicit non-closure:
  - 不改邮寄登记字段
  - 不做 envelope print query
  - 不改前端
- Remaining follow-up task ids:
  - `DOCDSP-BE-ENV-01`
  - `DOCDSP-FE-DISP-01`
  - `DOCDSP-FE-ENV-01`
  - `DOCDSP-QA-01`
