# MD-APP 申请人主数据 CRUD 设计说明

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`MD-PRE` 已经提供了 `Applicant` 的结构化承载、最小路由入口和只读 list skeleton，但当前仍缺少对象级 CRUD 闭环。`MD-APP` 第一轮目标是在既有 prerequisite 之上，为 `Applicant` 提供可用的 `list + create + update + enable/disable`，并把能力落在现有 settings/masterdata 入口，不扩展到任何下游引用联动。

## Assumptions

- `Applicant` 权威字段固定为：
  - `id`
  - `code`
  - `name_cn`
  - `name_en`
  - `is_active`
- 第一轮治理固定为：
  - `code` 唯一
  - `name_cn` 唯一
  - `is_active` 启停用
  - 不物理删除
- 页面落点固定为：
  - `frontend/src/modules/settings/pages/ApplicantList.vue`
- 第一轮不纳入：
  - case form 申请人切换
  - selector 启用项过滤
  - search/filter 扩展
  - import/export
  - 去重/合并/别名

## Scope

- 完成 `Applicant` 的对象级 CRUD 第一轮闭环：
  - `list`
  - `create`
  - `update`
  - `enable/disable`
- 完成对应 backend contract、service 校验与 frontend 页面交互

## Explicit Non-scope

- selector / case form / search / import / export 联动
- `detail`
- `delete`
- 别名、去重、合并、历史治理

## Exact Object / Field Inventory

### Applicant

- `id`
- `code`
- `name_cn`
- `name_en`
- `is_active`

## Governance Rules

- `code` 唯一
- `name_cn` 唯一
- 通过 `is_active` 执行启停用
- 不开放物理删除

## Exact CRUD Boundaries

- `list`
- `create`
- `update`
- `enable/disable`

当前明确不做：

- `detail`
- `delete`

## Model-layer Impact

- 基于 `MD-PRE` 已建立的 `Applicant` 结构化承载
- 本 story 不新增 schema / migration

## API / Service Impact

- 在现有 `applicants` 模块上补齐：
  - `POST /applicants`
  - `PUT /applicants/{applicant_id}`
  - `PUT /applicants/{applicant_id}/deactivate`
- 复用现有 list contract
- 增加唯一性与 not-found 业务校验

## UI / Permission Impact

- 在现有 `ApplicantList.vue` 上补齐：
  - 列表
  - 新建表单
  - 编辑表单
  - 启停用操作
- 权限沿用：
  - `Applicant.Read`
  - `Applicant.Write`

## Downstream Impact

当前明确不进入：

- `cases`
- `selectors`
- `search`
- `import/export`

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：可行
- 本 story 不新增 schema / migration，因此可在当前约束下作为对象级 CRUD story 推进

## Risks / Blockers / Prerequisite Tasks

- scope creep 风险高，尤其是 case 申请人切换和 selector 联动
- `ApplicantList.vue` 当前只是占位页，需避免做成“半 settings 壳增强”
- 字段口径必须继续对齐 prerequisite 的 `name_cn / name_en`，不能回退为未冻结的 `name`

## Exact Closure Slice Candidates

建议冻结为：

`在已建立的 Applicant 主数据承载与 settings/masterdata 骨架之上，完成 Applicant 对象的第一轮 CRUD 闭环，包括 list、create、update、enable/disable，并落在 ApplicantList.vue 的稳定入口上。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
