# Documents Step1-2 Wizard Design

## Story Shape Classification

- `shared_file_density`: `medium-high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `high`
- `chosen_runbook`: `P0-frontend-heavy-story`

## Problem Statement

当前仓库只有单条中间文件创建表单，缺少 spec 3.4 定义的批量录入向导。`P1 #8` 的最小可执行解释应先补齐 Step 1-2：允许用户一次输入多个案件，设定一组共享默认值，再逐案补充当前模型可承载的最小字段并一次性批量创建多条 `T_Document`。

## Assumptions

- 当前故事只覆盖 Step 1 与 Step 2。
- Step 1 第一版只支持逐行输入案卷号或申请号，不支持从案件查询结果导入。
- 行解析失败不阻断整批；成功行继续，失败行保留错误原因。
- `DocType / TemplateCode / DispatchDate` 在 Step 1 作为整批共享默认值。
- Step 2 允许逐案调整 `DispatchDate`，不允许逐案改 `DocType / TemplateCode`。
- Step 2 最小字段集收窄为当前模型可承载字段：
  - `DocName` -> `title`
  - `DispatchDate` -> `doc_date`
  - `InternalDocNo` -> `ref_no`
  - `NeedReply`
  - `ReplyToID`
  - `Remark / Summary / 简单补充信息` -> `extra_data`
- 当前故事不单独实现 `NeedNotifyAgent` 的持久化字段。
- 复杂动态扩展字段不实现；Step 2 仅提供一个面向 `extra_data` 的补充输入区。
- 向导状态只保存在前端内存，不做草稿持久化。
- 点击完成时通过新的批量 endpoint 一次性提交。

## Scope / Non-Scope

### In Scope

- 向导 UI shell 与 stepper
- Step 1 批量案件输入、解析、错误回显
- Step 2 逐案编辑当前 contract 可承载的最小字段集
- 向导批量创建 API / schema / service 编排
- 一次性批量创建多条 `T_Document`

### Explicit Non-Scope

- Step 3 时限任务预览或调整
- Step 4 费用草单预览或勾选
- Step 5 附件上传、模板渲染、自动存档 UI
- 草稿持久化
- 案件查询结果导入
- 复杂动态扩展字段引擎
- 邮寄信息批量登记
- schema / migration 变更
- `NeedNotifyAgent` 独立字段持久化

## Exact 5-Step Interpretation

- Step 1：选择案件、文件类型、模板、发文日
- Step 2：逐案编辑待创建文档的最小字段集（仅限当前 contract 可承载字段）
- Step 3：任务生成逻辑保持现有后端副作用，不纳入本故事 UI
- Step 4：费用草单联动保持现有后端副作用，不纳入本故事 UI
- Step 5：附件与模板生成不纳入本故事

## Impact

### Domain / API / Service

- 新增一个面向向导的批量创建 endpoint，负责统一校验和批量创建编排。
- 复用现有 document 创建规则、模板默认值、reply chain、任务生成、费用联动。
- 不修改现有单条 `POST /documents` 语义。

### UI

- 新增单独的向导页面，采用两步结构。
- Step 1 负责案件解析结果与批次共享字段。
- Step 2 负责逐案行编辑与提交。
- 所有用户可见文案使用简体中文。

## Compatibility Assessment

- `SQLite PoC`: compatible，当前设计不要求 schema 变更。
- `Phase 3 / 3.1 / 3.5`: compatible，前提是不新增 migration，仅做 API / service / frontend。

## Risks / Blockers

- `DocTemplate.input_fields` 若包含复杂动态配置，本故事只提供文本级补充，不做字段级动态渲染。
- 现有 `POST /documents` 的任务/费用副作用会继续发生；若实施中发现破坏当前最小闭环，需要回到 planning，拆出 prerequisite。
- `frontend/src/modules/documents/pages/DocumentWizard.vue` 预计会成为多个 FE 原子任务共享文件，必须串行 wave 执行。

## Exact Closure Slice Candidates

- 故事级 closure：
  - 中间文件向导 Step 1-2：批量解析案件、逐案补录当前 contract 可承载的最小字段、一次性批量创建 `T_Document`。
- 故事级 non-closure：
  - Step 3/4/5 的完整 UI 与复杂 documents lifecycle。

## Final Design Judgment

`可在当前约束下拆成可执行原子任务`
