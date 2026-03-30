# DOCDSP-BE-ENV-01 — 信封打印数据 query

- Source: `docs/superpowers/plans/2026-03-30-documents-dispatch-prereq.md`
- Type: `backend query`
- Execution mode: Atomic

## Task Definition

- Goal: 为单文档生成信封打印所需的即时地址数据。
- Exact closure slice:
  - envelope preview request/response contract
  - 地址优先级解析
- Explicit non-closure:
  - 不做交接单生成
  - 不做打印日志持久化
  - 不改前端
- Remaining follow-up task ids:
  - `DOCDSP-FE-ENV-01`
  - `DOCDSP-QA-01`
