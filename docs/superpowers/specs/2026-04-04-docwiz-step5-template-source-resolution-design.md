# DOCWIZ-STEP5-TEMPLATE-SOURCE-01 Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `backend prerequisite implementation before Step 5 final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`DOCWIZ-STEP5-FINAL-SUBMIT-01` 需要在最终完成向导时为 Step 5 已确认的附件候选生成真实文件并写入 `T_DocAttachment`。当前 blocker 不是 FE/BE 接线，而是 documents 模块缺少一个稳定的 `DocTemplate -> Template.file_path` 解析契约。

当前 repo 已有：

- `T_DocTemplate`
  - [backend/app/modules/documents/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/models.py)
- `T_Template`
  - [backend/app/modules/templates/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/templates/models.py)
- docx 渲染 carrier
  - [backend/app/modules/templates/render.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/templates/render.py)
  - [backend/app/common/doc_render/renderer.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/common/doc_render/renderer.py)

但当前没有任何现成 service contract 定义：

- 用哪个 `Template` 记录承接某个 `DocTemplate`
- 如何确定匹配规则
- 如何在匹配失败时返回 deterministic business error

## Assumptions

- 权威对象固定为：
  - `Step 5 template source resolver prerequisite implementation`
- 当前不允许 schema change
- resolver 必须消费现有 `Template` 字段：
  - `name`
  - `group`
  - `enabled`
  - `file_path`
- 当前结果形态固定为：
  - `backend service rule + targeted tests`

## Scope

- 冻结并实现 `DocTemplate -> Template.file_path` 的 deterministic resolver
- 冻结匹配规则、失败语义、文件存在性校验
- 为后续 Step 5 final submit 提供 implementation-ready carrier

## Explicit Non-scope

- 不做 Step 5 final submit integration
- 不生成真实 `DocAttachment`
- 不修改 `DocTemplate` / `Template` schema
- 不改前端

## Current Evidence

### Existing template registry

- [backend/app/modules/templates/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/templates/models.py)
  - `Template.name`
  - `Template.group`
  - `Template.language`
  - `Template.file_path`
  - `Template.enabled`

### Existing template storage convention

- [backend/app/modules/templates/docs/tpl_00_overview.md](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/templates/docs/tpl_00_overview.md)
  - `Template files stored under storage/templates/`

### Existing render carrier

- [backend/app/modules/templates/render.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/templates/render.py)
- [backend/app/common/doc_render/renderer.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/common/doc_render/renderer.py)

### Existing blocker

- `DocTemplate` has no template-source field
- `Template` has no `code`
- test seed currently creates `DocTemplate`, but not matching `Template`

## Resolver Contract

### Matching rule

- Resolver consumes a `DocTemplate`
- It looks for exactly one enabled `Template` where:
  - `Template.group == "DOC_TEMPLATE"`
  - `Template.name == DocTemplate.code`

### Why this rule

- `DocTemplate.code` is already unique and stable
- `Template.name` already exists and requires no schema change
- `Template.group` already exists and can scope the lookup away from billing or other template families
- Matching by `DocTemplate.name` would be weaker because name is display text and not guaranteed unique

### Failure semantics

- no match:
  - `DOCUMENT_TEMPLATE_SOURCE_NOT_FOUND`
  - `409`
- multiple matches:
  - `DOCUMENT_TEMPLATE_SOURCE_CONFLICT`
  - `409`
- resolved path missing on disk:
  - `DOCUMENT_TEMPLATE_FILE_NOT_FOUND`
  - `409`
- disabled template:
  - excluded from match set

## Implementation Recommendation

- add a documents service helper that:
  - loads the matching `Template`
  - resolves `file_path` relative to `backend/storage/templates/` when needed
  - verifies the final path exists
  - returns the absolute template path plus matched metadata
- add targeted backend tests for:
  - exact successful resolution
  - not found
  - conflict
  - file missing

## Exact Closure Slice

- `DOCWIZ-STEP5-TEMPLATE-SOURCE-01`
  - implement deterministic template-source resolution for Step 5 prerequisites

## Explicit Non-closure

- no attachment persistence helper
- no final attachment generation
- no frontend changes
- no schema change

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
