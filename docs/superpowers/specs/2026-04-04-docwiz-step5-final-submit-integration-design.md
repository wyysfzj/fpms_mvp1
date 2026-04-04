# DOCWIZ-STEP5-FINAL-SUBMIT-01 Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared FE/BE final-submit integration after Step 5 preview`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

当前 Step 5 preview 已经存在，但最终批量提交链仍然不会消费用户在 Step 5 中编辑过的字段，也不会在完成向导时实际渲染模板并创建真实 `DocAttachment`。这一轮需要完成 `DOCWIZ-STEP5-FINAL-SUBMIT-01`：让 Step 5 preview edits 进入最终 payload，并由后端在创建真实 `Document` 后解析模板来源、构建渲染上下文、生成附件字节并持久化到 `DocAttachment`。

## Assumptions

- 权威对象固定为：
  - `Step 5 final-submit integration`
- 结果形态固定为：
  - `shared FE/BE final-submit integration slice`
- 最小闭环固定为：
  - FE submits Step 5 edits
  - BE validates Step 5 attachment rows
  - explicit values override preview defaults
  - BE renders and persists generated attachments during final submit

## Scope

- FE 提交 Step 5 附件编辑值
- BE 接收并校验 Step 5 附件行
- 最终写入真实 `DocAttachment` 时消费显式值
- 通过既有 helper 串联模板来源解析、渲染上下文、附件持久化

## Explicit Non-scope

- `dispatch / envelope`
- `document search / reporting / status work`
- `single-document attachment page enhancements`
- `schema or migration changes`

## Current Integration Gap

### Frontend gap

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue) 中 Step 5 preview edits 目前只存在于内存态
- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts) 的最终提交 payload 目前没有 `attachment_rows`

### Backend gap

- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
  - `create_document_wizard_batch(...)` 还没有消费 Step 5 final rows
  - 还没有在最终提交链中调用模板解析、渲染与附件持久化 helper
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
  - `/documents/wizard/batch-create` 尚未承载 Step 5 final rows schema

## Shared-file / Ownership Analysis

### Frontend shared files

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts)
- [documents.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.types.ts)

### Backend shared files

- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
- [schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/schemas.py)
- [test_document_wizard_batch_create.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/tests/test_document_wizard_batch_create.py)

### Serialization rule

This story must stay split into:
- `BE final-submit carrier`
- `FE final payload wiring`
- `QA close`

It MUST NOT be executed as one mixed atomic task.

## Implementation Recommendation

### Preferred batch

- `DOCWIZ-STEP5-BE-FINAL-01`
  - extend final submit schema and backend write path for Step 5 attachment rows
- `DOCWIZ-STEP5-FE-FINAL-01`
  - include Step 5 edits in final payload
- `DOCWIZ-QA-STEP5-FINAL-01`
  - evidence audit and close summary

### Endpoint decision

- Continue extending existing `/documents/wizard/batch-create`
- Do NOT create a second finalization endpoint

## SQLite / Phase Compatibility Assessment

- No schema change
- No migration
- Uses existing carriers only
- Compatible with current Phase constraints

## Risks / Blockers

- Main risk: silently ignoring Step 5 preview edits and leaving them product-ineffective
- Main risk: creating attachment metadata without a real file path or bytes payload
- Main risk: absorbing dispatch / envelope or downstream attachment workflow into the same wave

## Exact Closure Slice Candidates

### Preferred slice family

- `DOCWIZ-STEP5-BE-FINAL-01`
- `DOCWIZ-STEP5-FE-FINAL-01`
- `DOCWIZ-QA-STEP5-FINAL-01`

### Explicit non-closure

- no dispatch / envelope
- no reporting / status work
- no single-document attachment page enhancement
- no schema change

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- Recommended execution starts with Step 5 final-submit integration.
