# CASEBF-FE-01 — 批件递交页面

- Source: `docs/superpowers/plans/2026-03-30-case-batch-filing-prereq.md`
- Type: `frontend workflow page`
- Execution mode: Atomic

## Task Definition

- Goal: 落地案件递交页面，支持筛选、勾选、参数输入和执行。
- Exact closure slice:
  - 批件递交独立页面
  - 最小筛选集
  - 列表勾选
  - `submitted_date / apply_exam_now` 参数区
  - 调用后端批量动作
- Explicit non-closure:
  - 不改 `CaseList.vue`
  - 不做递交清单文档
  - 不做 timeline
  - 不做 tasks/documents 联动 UI
- Remaining follow-up task ids:
  - `CASEBF-QA-01`
