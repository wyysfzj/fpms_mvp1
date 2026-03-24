# PE-FE-CS-02 执行摘要

## 执行任务
- Task ID: `PE-FE-CS-02`
- Task File: `tasks/postenhancement/frontend/PE-FE-CS-02.md`
- 执行范围：仅实现支出录入与列表页及对应 typed API。

## 修改文件（Allowlist）
- `frontend/src/modules/expenses/pages/ExpenseList.vue`
- `frontend/src/modules/expenses/pages/ExpenseCreate.vue`
- `frontend/src/api/expenses.ts`
- `frontend/src/api/expenses.types.ts`

## 实现要点
- 新增支出 API 类型与接口封装：
  - `getExpenses`（支持 `case_id/category/date_from/date_to` 等筛选）
  - `createExpense`
- 新增确定性中文错误映射：按 `status/code` 输出稳定中文错误文案，并保留字段级错误映射。
- 新增支出列表页：
  - 支持按案件/项目编号、类别、日期范围筛选
  - 支持分页、加载态、空态、错误态
  - 展示后端统计信息（总笔数/总金额/分类计数）
- 新增支出录入页：
  - 录入字段覆盖普通案件与顾问项目通用场景
  - 前端校验 + 后端字段错误映射

## 验证结果
- `cd frontend && npm run lint` → 通过（rc=0）
- `cd frontend && npm run typecheck` → 通过（rc=0）

详细日志见：
- `artifacts/PE-FE-CS-02/results.jsonl`
- `artifacts/PE-FE-CS-02/outputs/*`

## 预期接口状态码（联调）
- `GET /expenses`：`200`
- `POST /expenses`：`201`
- 错误场景：`400/401/403/404/409/422`

## 手工验证建议（UI）
- 进入支出列表页，按案件/类别/日期范围筛选，确认结果与分页变化正确。
- 进入支出录入页，提交合法数据后应提示成功并返回。
- 提交非法金额/缺失必填项，确认页面显示中文错误提示与字段错误。
