# P1 #8 中间文件 5 步向导 Step 5 Attachment / Template Generation Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared multi-lane residual contract before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`P1 #8 中间文件 5 步向导` 当前已经具备 Step 1/2 representative slices，并已分别冻结 Step 3 deadline linkage 与 Step 4 fee linkage。对于 residual program 的下一轮收口，当前最自然的 closure 不是继续扩页面，而是先冻结 `Step 5 – 附件 / 模板生成` 的 contract：哪些待创建 document 会进入 Step 5、Step 5 需要展示和允许调整哪些模板生成或附件字段、以及这些附件/模板生成在“完成向导”时如何与 document 创建统一落库。

## Assumptions

- 权威对象固定为：
  - `wizard Step 5 attachment/template-generation semantics`
- 现有单文档模板渲染或附件能力不自动等于 Step 5 已闭合
- Step 5 只消费已稳定的：
  - Step 1/2 draft document 集合
  - Step 3 contract
  - Step 4 contract
- 第一轮 residual choice 固定为：
  - `Step 5 attachment/template generation`
- 第一轮结果形态固定为：
  - `residual design / contract freeze`
- 第一轮最小闭环固定为：
  - Step 5 applicability
  - attachment/template candidate semantics
  - preview/edit boundary
  - final-write timing
  - explicit deferred ledger

## Scope

- 冻结 Step 5 的适用条件
- 冻结 Step 5 的 attachment/template candidate 语义
- 冻结 Step 5 UI 需展示/可调整字段的 contract
- 冻结 Step 5 与“最终完成向导”之间的写入关系

## Explicit Non-scope

- dispatch / envelope
- document search
- reporting/export
- downstream status transitions
- 任何 frontend/backend 实现补丁

## Current Page / API / Service Inventory

### Existing wizard shell and Step 1/2 slices

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
- [documents/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
  - `POST /documents/wizard/batch-create`
- [documents/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
  - `create_document_wizard_batch(...)`

### Existing Step 5-adjacent backend carriers

- [documents/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/models.py)
  - `DocAttachment`
  - `DocTemplate`
- [documents/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
  - `add_attachment(...)`
  - `get_attachment_download(...)`
- [tasks/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/api.py)
  - `DocxRenderer`
  - `render_docx_bytes(...)`

### Existing surrounding document capabilities that are NOT wizard closure

- attachment upload/download for single document:
  - [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts)
- dispatch / envelope:
  - [DocumentDispatch.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentDispatch.vue)
  - [DocumentEnvelopePrint.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentEnvelopePrint.vue)
- search:
  - [DocumentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentList.vue)

## Representative-slice Analysis

- Step 1/2 already prove:
  - wizard shell exists
  - batch defaults and row editing exist
  - batch create contract exists
- Existing attachment/template-adjacent carriers already prove:
  - single-document attachments can be persisted
  - repo has template-render capability in other modules
- Existing carriers do NOT prove:
  - Step 5 applicability inside the wizard
  - Step 5 candidate preview contract
  - Step 5 user-adjustment boundary
  - Step 5 final-write timing

## Residual Step Semantics Definition

### Applicable draft rows

Step 5 only applies to draft documents where:
- a usable template/render target exists
- and the draft row remains eligible for final document creation

### Candidate generation

For each applicable draft row, Step 5 must define:
- template source
- output attachment candidate source
- resulting preview fields
- whether candidate generation is deterministic and side-effect-free before final submit

### UI contract

Step 5 must freeze which fields are:
- preview-only
- user-adjustable
- derived but overridable

At minimum, the spec must decide the contract for:
- `CaseNo`
- `DocName`
- `TemplateCode`
- output file name
- output type / format
- whether to generate one candidate attachment
- any skip/disable control for one candidate artifact

### Final write timing

The spec must explicitly freeze whether:
- Step 5 only previews attachment/template candidates in-memory
- or creates temporary generated files before final submit

Current recommended interpretation:
- Step 5 preview stays in-memory
- real generated attachments / persisted files are written only on final wizard completion together with documents

## Step Dependency Options

### Option A — Step 5 consumes stable Step 3/4

- Freeze Step 5 after Step 3 and Step 4
- Step 5 does not redefine earlier step timing or applicability
- Recommended

### Option B — Step 5 independently reopens earlier steps

- Higher ambiguity
- Not recommended

## First-round Result Shape

- `Step 5 residual contract freeze`
- `narrowed follow-up mapping`

## Deferred Slices Ledger

- dispatch / envelope
- document search
- reporting/export
- downstream status transitions
- implementation patching of wizard UI/API/service

## Model-layer Impact

- No schema change is approved in this story
- Only contract interpretation over existing `Document` / `DocAttachment` / `DocTemplate` carriers

## API / Service Impact

- No API or service patch in this story
- But the frozen Step 5 contract must identify which existing attachment/template carriers a future implementation story will consume

## UI / Permission Impact

- No UI patch in this story
- But the frozen contract must state which Step 5 fields future UI may preview or edit

## Cross-module Impact

- `documents`
- `tasks`
- explicitly NOT `dispatch / search / reporting`

## SQLite / Phase Compatibility Assessment

- Compatible with current constraints because this is doc-only contract freeze
- If later implementation reveals missing runtime carrier or schema need, work must return to planning

## Risks / Blockers

- Main risk: treating existing single-document attachment or render support as if wizard Step 5 were already closed
- Main risk: silently absorbing dispatch / status transitions into the same story
- If the final-submit timing cannot be frozen without discovering new carrier gaps, the story must stop and split a prerequisite

## Exact Closure Slice Candidates

### Preferred slice

- `DOCWIZ-STEP5-SPEC-01`
  - freeze wizard Step 5 attachment/template-generation contract only

### Explicit non-closure

- no dispatch / envelope
- no search / reporting
- no implementation patch

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a doc-only residual contract freeze for wizard Step 5.
