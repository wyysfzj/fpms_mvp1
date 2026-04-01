# P2 #19 中间文件专项查询设计说明

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`DOCSEARCH-PRE-01` 已经冻结了 spec 9.3.2 与当前 repo 承载之间的稳定映射。基于该 prerequisite，`P2 #19` 的第一轮 query story 不再追求完整复刻 spec 的全部“中间文件查询”术语，而是只闭合当前 repo 已有 carrier 能稳定承载的 document-specific search：

- `TemplateCode`
- `DocName`
- `NeedReply`
- `已Reply / Reply`
- `CaseNo`
- `date`
- `direction`

本轮职责不是建设文书系统整体检索平台，也不是补齐 `DocType` 的独立 carrier，而是在现有 `documents list/query` 基础之上完成第一轮可执行查询增强与现有列表页收敛。

## Assumptions

- 当前权威查询对象只固定为：
  - spec 9.3.2 所指的“中间文件” `document records`
- 第一轮结果形态固定为：
  - `一个统一 document 明细列表`
- 已冻结的稳定映射为：
  - `TemplateCode` -> `DocTemplate.code`
  - `DocName` -> `Document.title`
  - `NeedReply` -> `Document.need_reply`
  - `已Reply / Reply` -> `Document.reply_date is not null`
- 第一轮 `direction` 语义固定为：
  - 仅使用 document 主表现有 `IN / OUT`
- 第一轮明确 deferred：
  - `DocType`
    - 当前无直接 carrier
    - 不在本轮 query story 闭环

## Scope

- documents query enhancement service
- documents query API contract enhancement
- documents response schema收敛
- 现有 `DocumentList` 页面专项查询增强
- documents 前端 api/types 收敛

## Explicit Non-scope

- `DocType` 独立筛选闭环
- `summary cards`
- `export`
- `print`
- `dispatch linkage`
- `reply-chain linkage`
- `reporting/dashboard`
- `full-text / OCR search`
- 新建独立文书检索系统

## Exact Source Tables / Field Inventory

### Source Objects

- `backend/app/modules/documents/models.py::Document`
- `backend/app/modules/documents/models.py::DocTemplate`
- `backend/app/modules/cases/models.py::Case`

### Executable First-round Projection

- `document_id`
  - 来源：`Document.id`
- `case_id`
  - 来源：`Document.case_id`
- `case_no`
  - 来源：`Case.case_no`
- `title`
  - 来源：`Document.title`
- `direction`
  - 来源：`Document.direction`
- `template_code`
  - 来源：`DocTemplate.code`
- `doc_date`
  - 来源：`Document.doc_date`
- `need_reply`
  - 来源：`Document.need_reply`
- `reply_date`
  - 来源：`Document.reply_date`
- `ref_no`
  - 来源：`Document.ref_no`

## Stable Mapping Summary

- `DocType` -> no direct carrier, never equate to `direction`; deferred
- `TemplateCode` -> `DocTemplate.code`
- `DocName` -> `Document.title`
- `NeedReply` -> `Document.need_reply`
- `已Reply` -> `Document.reply_date is not null`
- `Reply` -> display/query synonym for `已Reply`, not a new carrier

## Search Semantics

- 查询语义是：
  - 在现有 `Document` 承载上按冻结筛选集过滤
  - 联到 `Case` / `DocTemplate` 取得 `case_no / template_code`
  - 返回统一明细列表
- 第一轮 keyword 口径收敛为：
  - `DocName` -> `Document.title`
  - 不再把 `ref_no` 冒充 `DocName`
- 当前不要求：
  - `DocType` 独立查询
  - dispatch / reply 联查
  - 全文检索 / OCR

## First-round Result Shape

- 统一明细列表
- 分页
- 统一筛选区
- 不附带 summary cards

## First-round Filter Definition

- `template_code`
- `doc_name`
- `case_no`
- `need_reply`
- `replied`
- `date_range`
- `direction`

## Deferred Slices Ledger

- `DocType` 独立筛选
- `summary cards`
- `export`
- `print`
- `dispatch linkage`
- `reply-chain linkage`
- `reporting/dashboard`
- `full-text / OCR search`

## Model-layer Impact

- 不新增 schema
- 不新增 migration
- 复用现有 `Document` / `DocTemplate` / `Case` 承载

## API / Service Impact

- 在 `backend/app/modules/documents/service.py` 中补齐：
  - `case_no`
  - `template_code`
  - `doc_name`
  的稳定筛选
- 在 `backend/app/modules/documents/schemas.py` 中收敛第一轮列表投影
- 在 `backend/app/modules/documents/api.py` 中补齐专项查询参数
- 权限继续沿用现有 documents 读取权限

## UI / Permission Impact

- 复用 `frontend/src/modules/documents/pages/DocumentList.vue`
- 收敛 `frontend/src/api/documents.ts` / `documents.types.ts`
- 不新建 route/page
- 所有用户可见文案必须使用简体中文

## Cross-module Impact

当前明确不进入：

- `dispatch`
- `reply_chain`
- `attachments`
- `OCR`
- `reports`

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：必需
- 当前无 schema prerequisite
- 本 story 可作为标准 `BE -> FE` 查询增强条目执行

## Risks / Blockers / Prerequisite Tasks

- 最大风险是再次把 `DocType` 偷换成 `direction`
- 第二个风险是让 `doc_name` 搜索重新混入 `ref_no`
- 第三个风险是把 `Reply` 误实现成新的 carrier 或新字段
- 当前 prerequisite 已关闭：
  - `DOCSEARCH-PRE-01`

## Exact Closure Slice Candidates

建议冻结为：

`在现有 documents list/query 基础之上，完成基于已冻结映射的第一轮 document-specific search，包括 template_code / doc_name / case_no / need_reply / replied / date / direction 的 query contract，以及现有 DocumentList 页面上的专项查询增强。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
