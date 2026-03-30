# P2 #14 主数据前置依赖（Applicant / Country）设计说明

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `chained (DB -> BE skeleton -> FE skeleton)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

当前仓库缺少 `Applicant` 与 `Country` 的稳定主数据承载、后端 contract 和 settings/masterdata 落点。现有系统只有 `Client` 主数据模式可复用，而 `Applicant` 仍是案件从属自由录入事实，`Country` 仍是多个模块中的 plain code/string。  
因此，`P2 #14` 不能直接诚实地进入对象级 CRUD，而应先完成共享 prerequisite：结构化承载判定、是否需要新模型/新表、最小 settings/masterdata 骨架、权限命名空间和后续 CRUD 共用 contract 形状。

## Assumptions

- `P2 #14` 已拆为：
  - `MD-PRE`
  - `MD-CTR`
  - `MD-APP`
- `MD-PRE` 只处理共享 prerequisite。
- 两个对象都应使用独立结构化承载，不允许 `extra_data` 兜底。
- 第一轮治理默认值固定为：
  - `enable/disable`
  - 不优先物理删除
  - 编码唯一
  - 名称唯一
- 第一轮只冻结：
  - 主数据承载方式
  - schema necessity
  - settings/masterdata 路由入口骨架
  - `Applicant / Country` 独立 read/write 权限命名空间
  - 后续 CRUD 共用 contract 形状

## Scope

- 判定并建立 `Applicant / Country` 的结构化主数据承载基础
- 若需要，增加对应模型/表与 SQLite-safe migration
- 冻结共享 CRUD contract 形状
- 冻结独立权限命名空间
- 建立最小 settings/masterdata 路由入口骨架

## Explicit Non-scope

- `Applicant` 完整 CRUD
- `Country` 完整 CRUD
- case form / selector / search / import / export 联动
- 完整权限矩阵接线
- 历史治理、去重、合并

## Exact Object / Field Inventory

### Applicant

- 共享 prerequisite 仅冻结最小承载字段：
  - `id`
  - `code`
  - `name_cn`
  - `name_en`
  - `is_active`

### Country

- 共享 prerequisite 仅冻结最小承载字段：
  - `id`
  - `code`
  - `name_cn`
  - `name_en`
  - `is_active`

## Governance Rules

- 第一轮优先 `enable/disable`
- 不优先物理删除
- `code` 唯一
- 核心名称唯一
- 不引入历史别名
- 不引入去重/合并/清洗逻辑

## Exact CRUD Boundaries

`MD-PRE` 不实现对象级 CRUD，只冻结后续 `MD-APP / MD-CTR` 共享 contract 形状：

- `list`
- `create`
- `update`
- `enable/disable`

当前明确不做：

- `detail`
- `delete`

## Model-layer Impact

- 高概率需要新增：
  - `Applicant` 结构化模型/表
  - `Country` 结构化模型/表
- 需要 SQLite-safe migration
- 需要复用现有 `Client` 主数据模式，而不是重用 case 从属事实表

## API / Service Impact

- 冻结后续 CRUD 的共享 contract 形状
- 冻结模块边界与命名空间
- 最小骨架允许后续对象 story 在稳定 contract 上实现
- 本 story 不完成完整对象 CRUD

## UI / Permission Impact

- 建立最小 settings/masterdata 路由入口骨架
- 冻结未来对象页面挂载位置
- 权限命名空间：
  - `Applicant.Read`
  - `Applicant.Write`
  - `Country.Read`
  - `Country.Write`

## Downstream Impact

当前明确不进入：

- `cases`
- `selectors`
- `search`
- `import/export`

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：可行，但若新增表必须使用 SQLite-safe migration
- 若按本设计执行，明确包含承载判定与潜在新表，因此不是当前无 schema Phase 可直接完成的小改

## Risks / Blockers / Prerequisite Tasks

- `Applicant / Country` 在 repo 中都不是成熟主数据对象
- `settings` 壳本身不成熟，只能做最小入口骨架
- 若不先冻结 prerequisite，`MD-APP / MD-CTR` 会各自发明模型、权限、路由和 contract

## Exact Closure Slice Candidates

建议冻结为：

`冻结 Applicant / Country 共享的主数据 prerequisite：确认结构化承载方式、是否需要新模型/新表、settings/masterdata 最小路由入口骨架、独立 read/write 权限命名空间，以及后续对象级 CRUD 的共享 contract 形状。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
- 但这是 prerequisite story，不是对象级 CRUD story
