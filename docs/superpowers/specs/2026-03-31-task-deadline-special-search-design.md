# P2 #17 专项检索设计说明

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

当前 repo 已具备通用 `Task` 承载、通用任务列表和今日提醒视图，但缺少一个针对 `APPLY_FEE_LIMIT` 与 `EXAM_REQUEST_LIMIT` 的专项检索能力。`P2 #17` 的第一轮职责不是做任务提醒与分析平台，而是在现有 `Task` 承载之上提供专项 deadline search，包括冻结 task code 边界、统一投影、简单 overdue 语义、最小筛选集和专属专项检索页面。

## Assumptions

- 当前权威检索对象只固定为：
  - `APPLY_FEE_LIMIT`
  - `EXAM_REQUEST_LIMIT`
- 第一轮结果形态固定为：
  - `一个统一 task 明细列表`
- 第一轮 unified projection 固定为：
  - `task_code`
  - `task_id`
  - `case_id`
  - `case_no`
  - `client_name`
  - `title`
  - `status`
  - `due_date`
  - `is_overdue`
  - `remark`
- 第一轮 overdue 语义固定为：
  - `due_date < today && status != DONE`
- 第一轮搜索语义固定为：
  - 在现有 `Task` 承载上过滤
  - 带 `case / client` 联表投影
  - 不做 reminder 联查
  - 不做 workflow 动作视图
- 第一轮最小筛选集固定为：
  - `task_code`
  - `status`
  - `case_no`
  - `client_name`
  - `due_date_range`
  - `is_overdue`
- 第一轮 deferred slices 固定为：
  - `summary cards`
  - `export`
  - `print`
  - `reminder linkage`
  - `dashboard/reporting`
  - `批量动作`

## Scope

- tasks 模块专项检索 service
- tasks 模块专项检索 API contract
- tasks 模块专项检索 response schema
- 专属专项检索页面
- tasks 前端 api/types、route、menu 落点

## Explicit Non-scope

- `summary cards`
- `export`
- `print`
- `reminder linkage`
- `dashboard/reporting`
- `批量动作`
- 其他 task code 的通用检索平台化改造

## Exact Source Tables / Field Inventory

### Source Objects

- `backend/app/modules/tasks/models.py::Task`
- `backend/app/modules/tasks/models.py::TaskTemplate`
- `backend/app/modules/cases/models.py::Case`
- `backend/app/modules/masterdata/clients/models.py::Client`

### Unified Projection

- `task_code`
  - 来源：`TaskTemplate.code`
- `task_id`
  - 来源：`Task.id`
- `case_id`
  - 来源：`Task.case_id`
- `case_no`
  - 来源：`Case.case_no`
- `client_name`
  - 来源：`Client.name_cn`
- `title`
  - 来源：`Task.title`
- `status`
  - 来源：`Task.status`
- `due_date`
  - 来源：`Task.due_date`
- `is_overdue`
  - 来源：由 `due_date < today && status != DONE` 派生
- `remark`
  - 当前第一轮来源：占位可空字段
  - 现有 `Task` carrier 未持久化该列，允许返回 `null`

## Overdue Semantics Definition

- 第一轮 overdue 仅是简单派生字段：
  - `Task.due_date` 早于查询当日
  - 且 `Task.status != DONE`
- 当前不绑定：
  - reminder 发送记录
  - reminder 状态
  - 其他扩展关闭类状态

## Search Semantics

- 查询语义是：
  - 在现有 `Task` 承载上按专项 task code 过滤
  - 限定 `TaskTemplate.code in {APPLY_FEE_LIMIT, EXAM_REQUEST_LIMIT}`
  - 在 service 层完成 case/client 联表投影
- 当前不要求：
  - reminder 联查
  - workflow 动作入口
  - dashboard/reporting 聚合

## First-round Result Shape

- 统一明细列表
- 分页
- 最小筛选区
- 不附带 summary cards
- 不做 tabs / grouped sections

## First-round Filter Definition

- `task_code`
- `status`
- `case_no`
- `client_name`
- `due_date_range`
  - backend contract 允许以 `due_date_from` / `due_date_to` 两个 query param 落地
- `is_overdue`

## Deferred Slices Ledger

- `summary cards`
- `export`
- `print`
- `reminder linkage`
- `dashboard/reporting`
- `批量动作`

## Model-layer Impact

- 不新增 schema
- 不新增 migration
- 复用现有 `Task` / `TaskTemplate` / `Case` / `Client` 承载

## API / Service Impact

- 在 `backend/app/modules/tasks/service.py` 中增加专项检索 service
- 在 `backend/app/modules/tasks/schemas.py` 中增加专项检索 projection schema
- 在 `backend/app/modules/tasks/api.py` 中增加专项检索 endpoint
- 权限建议：
  - endpoint 使用 `Task.Read`

## UI / Permission Impact

- 新增 tasks 模块专项检索页面
- 新增 `frontend/src/api/tasks.ts` / `tasks.types.ts` 中的专项检索 client/types
- 新增 tasks route 与 menu 落点
- 所有用户可见文案必须使用简体中文

## Cross-module Impact

当前明确不进入：

- `reminders`
- `dashboard`
- `reporting`
- `documents`
- 其他 task workflow 动作

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：必需
- 当前无明显 schema prerequisite
- 本 story 可作为标准 `BE -> FE` 查询条目执行

## Risks / Blockers / Prerequisite Tasks

- 最大风险是把专项检索漂移成通用 task search / reminder/reporting 平台
- 第二个风险是把 overdue 语义与 reminder 状态绑定
- 第三个风险是把专项检索硬塞进现有 `TaskList.vue` 或 `TodayReminders.vue`
- 第四个风险是把 `remark` 误当成现有持久化 task 字段；当前第一轮只能诚实地将其视为可空占位字段
- 当前无单独 prerequisite task 要求

## Exact Closure Slice Candidates

建议冻结为：

`在现有 Task 承载之上，提供一个针对 APPLY_FEE_LIMIT / EXAM_REQUEST_LIMIT 的第一轮专项检索，包括 task search contract、统一明细列表、最小筛选集、简单 overdue 派生语义，以及专属专项检索页面。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
