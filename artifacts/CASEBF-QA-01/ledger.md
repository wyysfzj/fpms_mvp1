# CASEBF Item-to-Slice Ledger

## Scope Interpretation
- Story: `P2 #11 批件递交 (US-CM-05) / Cases Batch Filing Workflow`
- Approved closure:
  - 按最小筛选集查询 `NOT_FILED` 候选案件
  - 批量提交 `selected_case_ids / submitted_date / apply_exam_now`
  - `Case.status: NOT_FILED -> WAITING_RECEIPT`
  - 当 `apply_exam_now=true` 时更新 `has_exam_request=true`
- Explicit non-closure:
  - `generate_list` 文档生成
  - documents/tasks/billing/reminders/report/timeline 联动
  - 历史回填/批量修复

## Slice Mapping

### CASEBF-DB-01
- Required slice:
  - `Case.submitted_date` 结构化承载
- Evidence:
  - `artifacts/CASEBF-DB-01/summary.md`
  - `artifacts/CASEBF-DB-01/git/diff.patch`
- Close decision:
  - `covered`

### CASEBF-BE-QUERY-01
- Required slice:
  - 批件递交页面专用候选案件查询
  - 最小筛选集
  - 最小列表字段
- Evidence:
  - `artifacts/CASEBF-BE-QUERY-01/summary.md`
  - `artifacts/CASEBF-BE-QUERY-01/git/diff.patch`
- Close decision:
  - `covered`

### CASEBF-BE-ACT-01
- Required slice:
  - 批量执行递交动作
  - `submitted_date` 写入
  - `NOT_FILED -> WAITING_RECEIPT`
  - `has_exam_request` 条件更新
- Evidence:
  - `artifacts/CASEBF-BE-ACT-01/summary.md`
  - `artifacts/CASEBF-BE-ACT-01/git/diff.patch`
- Close decision:
  - `covered`

### CASEBF-FE-01
- Required slice:
  - 独立批件递交页面
  - 最小筛选 UI
  - 候选列表勾选
  - `submitted_date / apply_exam_now` 参数区
  - 调用后端批量动作
- Evidence:
  - `artifacts/CASEBF-FE-01/summary.md`
  - `artifacts/CASEBF-FE-01/git/diff.patch`
- Close decision:
  - `covered`

## Residual Gap
- None inside the approved interpretation
- Remaining non-closure is explicit and deferred:
  - `generate_list`
  - documents/tasks downstream linkage
  - timeline/report enhancements
