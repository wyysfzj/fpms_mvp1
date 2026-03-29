# CASEBF-BE-ACT-01 — 批件递交执行动作

- Source: `docs/superpowers/plans/2026-03-30-case-batch-filing-prereq.md`
- Type: `backend business workflow`
- Execution mode: Atomic

## Task Definition

- Goal: 执行案件递交批处理动作并完成状态迁移。
- Exact closure slice:
  - 接收 `selected_case_ids / submitted_date / apply_exam_now`
  - 校验并批量执行 `NOT_FILED -> WAITING_RECEIPT`
  - 更新 `submitted_date`
  - 条件更新 `has_exam_request`
- Explicit non-closure:
  - 不生成递交清单文档
  - 不生成申请费时限任务
  - 不改前端
  - 不做历史回填
- Remaining follow-up task ids:
  - `CASEBF-FE-01`
  - `CASEBF-QA-01`
