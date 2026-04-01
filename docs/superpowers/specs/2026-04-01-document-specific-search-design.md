# P2 #19 中间文件专项查询设计说明

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `chained (PRE -> BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

当前 repo 已经具备通用 `documents` 列表与筛选能力，但还没有按 spec 9.3.2 冻结过的“中间文件专项查询” closure。更关键的是，spec 中的核心查询维度和当前 repo 的真实承载并不完全一致：

- spec 强调：
  - `DocType`
  - `TemplateCode / DocName`
  - `NeedReply / 是否已 Reply`
- 当前 repo 真实承载更接近：
  - `direction`
  - `doc_template_id`
  - `title / ref_no`
  - `need_reply / replied`

因此 `P2 #19` 不能直接按“现有 `/documents` 多加几个 query param”执行，必须先做一个最小 prerequisite，把 spec 口径和 repo 承载的稳定映射冻结下来，然后再进入 query enhancement story。

## Assumptions

- 当前权威查询对象只固定为：
  - spec 9.3.2 所指的“中间文件” `document records`
- 当前明确不纳入：
  - `dispatch`
  - `reply-chain`
  - `attachments`
  - `OCR`
  - `full-text search`
- 第一轮结果形态仍固定为：
  - `一个统一 document 明细列表`
- 第一轮 `direction` 语义仍固定为：
  - 仅使用 document 主表现有 `IN / OUT`
- 当前最大的前置问题不是 schema，而是以下映射尚未冻结：
  - `DocType` 在当前 repo 中的真实来源
  - `TemplateCode / DocName` 与当前 `doc_template_id / title / ref_no` 的稳定映射
  - `NeedReply / 已回复` 是否就是本条第一轮的权威“状态类”筛选

## Scope

- 先关 `DOCSEARCH-PRE-01`
- 冻结 spec 9.3.2 查询条件和当前 repo 承载的稳定映射
- 在 prerequisite 之后，再执行 query enhancement story

## Explicit Non-scope

- 直接开始实现 `P2 #19` 全部 query story
- 新建文书检索子系统
- 吸收 `dispatch / reply / reporting / OCR / export`

## Exact Source Tables / Field Inventory

### Source Objects

- `backend/app/modules/documents/models.py::Document`
- `backend/app/modules/documents/models.py::DocTemplate`
- `backend/app/modules/cases/models.py::Case`

### Current Carrier Facts

- `Document` 当前有：
  - `direction`
  - `doc_date`
  - `title`
  - `ref_no`
  - `need_reply`
  - `reply_date`
  - `doc_template_id`
- `Document` 当前没有独立持久化：
  - `DocType` enum
  - 文书主表 `status`
  - `template_code` 直出列
  - 文书主表 `remark`
- `DocTemplate.code` 已存在，但必须通过联结取得
- 前端当前的 `doc_type` 字段实际映射到 `ref_no`

## Mapping Prerequisite

在继续实现 query story 之前，必须先冻结以下映射：

- `DocType`
  - 当前不直接由单一 carrier 承载
  - 不要把它等同为 `direction`
  - 仅在后续 query contract 中按 spec 语义保留为独立筛选项，必要时由组合投影解释，但本 prereq 不新增 carrier
- `TemplateCode`
  - 冻结为 `DocTemplate.code`
- `DocName`
  - 冻结为 `Document.title`
- `NeedReply`
  - 冻结为 `Document.need_reply`
- `已Reply`
  - 冻结为 `Document.reply_date is not null`
- `Reply`
  - 在本次冻结中仅作为 `已Reply` 的展示/过滤语义，不引入新的 reply-chain carrier

### Stable Carrier Mapping Summary

- `DocType` -> no direct carrier, never equate to `direction`
- `TemplateCode` -> `DocTemplate.code`
- `DocName` -> `Document.title`
- `NeedReply` -> `Document.need_reply`
- `已Reply` -> `Document.reply_date is not null`

## Deferred Slices Ledger

- `summary cards`
- `export`
- `print`
- `dispatch linkage`
- `reply-chain linkage`
- `reporting/dashboard`
- `full-text / OCR search`

## Model-layer Impact

- 当前没有证据表明必须先做 schema prerequisite
- 当前更像 `contract mapping prerequisite`
- 若后续冻结表明 `DocType` 必须有独立 carrier，才再升级为 schema prerequisite

## API / Service Impact

- `DOCSEARCH-PRE-01` 只冻结 contract mapping，不闭合最终 query contract
- backend/frontend implementation remains blocked until this prerequisite closes
- `DOCSEARCH-BE-01` 等待 prerequisite 后再实现：
  - documents query params
  - service filter / joins / projection

## UI / Permission Impact

- `DOCSEARCH-PRE-01` 不做前端
- `DOCSEARCH-FE-01` 等待 prerequisite 后再实现
- 权限继续沿用现有 documents 读取权限，不新增专项权限命名空间

## Cross-module Impact

当前明确不进入：

- `dispatch`
- `reply_chain`
- `attachments`
- `OCR`
- `reports`

## SQLite / Phase Compatibility Assessment

- SQLite 兼容：必需
- 当前未发现明确 migration prerequisite
- 但当前存在明显 contract prerequisite

## Risks / Blockers / Prerequisite Tasks

- 最大风险是把现有 generic documents list 误判为已经自动满足 spec 9.3.2
- 第二个风险是把 `DocType / status / template_code` 直接按 spec 名称写进 contract，但 repo 实际没有对应 carrier
- 第三个风险是把 `NeedReply / replied` 这组现有业务语义错误替换成一个新的 `status`

当前 prerequisite task：

- `DOCSEARCH-PRE-01`
  - 冻结 `DocType / TemplateCode / DocName / NeedReply / Reply` 在当前 repo 的稳定映射

## Exact Closure Slice Candidates

当前 program-level 建议冻结为：

`先完成 spec 9.3.2 查询条件与当前 documents repo 承载的稳定映射 prerequisite，再在其基础上实现第一轮 document-specific query enhancement。`

其中 prerequisite story 冻结为：

`冻结 spec 9.3.2 中 DocType、TemplateCode/DocName、NeedReply/Reply 与当前 Document/DocTemplate/Case 承载的稳定映射，为后续 document-specific search backend/frontend story 提供可执行 contract。`

## Final Design Judgment

- `不可直接实现，必须先新增 prerequisite task(s)`
