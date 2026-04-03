# P1 #8 中间文件 5 步向导 Step 4 Fee Linkage Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared multi-lane residual contract before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`P1 #8 中间文件 5 步向导` 当前已经具备 Step 1/2 representative slices，并已用 `DOCWIZ-STEP3-SPEC-01` 冻结 Step 3 deadline linkage。对于 residual program 的下一轮收口，当前最自然的 closure 不是继续扩页面，而是先冻结 `Step 4 – 费用联动` 的 contract：哪些待创建 document 会进入 Step 4、Step 4 需要展示和允许调整哪些费用草稿字段、以及这些费用草稿在“完成向导”时如何与 document 创建统一落库。

## Assumptions

- 权威对象固定为：
  - `wizard Step 4 fee linkage semantics`
- `fee_draft_type / fee_item_list / fee_linking_service` 不自动等于 Step 4 已闭合
- Step 4 只消费已稳定的：
  - Step 1/2 draft document 集合
  - Step 3 contract
- 第一轮 residual choice 固定为：
  - `Step 4 fee linkage`
- 第一轮结果形态固定为：
  - `residual design / contract freeze`
- 第一轮最小闭环固定为：
  - Step 4 applicability
  - fee draft candidate semantics
  - preview/edit boundary
  - final-write timing
  - explicit deferred ledger

## Scope

- 冻结 Step 4 的适用条件
- 冻结 Step 4 的 fee candidate 生成语义
- 冻结 Step 4 UI 需展示/可调整字段的 contract
- 冻结 Step 4 与“最终完成向导”之间的写入关系

## Explicit Non-scope

- Step 5 attachment/template generation
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

### Existing Step 4 backend carriers

- [documents/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/models.py)
  - `DocTemplate.fee_draft_type`
  - `DocTemplate.fee_item_list`
- [documents/fee_linking_service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/fee_linking_service.py)
  - fee draft auto-creation support
  - fee item parsing support
- [documents/schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/schemas.py)
  - `fee_draft_type`
  - `fee_item_list`

### Existing surrounding document capabilities that are NOT wizard closure

- single-document fee hints:
  - [DocumentCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentCreate.vue)
  - [DocumentEdit.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentEdit.vue)
  - [DocumentDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentDetail.vue)
- dispatch / envelope:
  - [DocumentDispatch.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentDispatch.vue)
  - [DocumentEnvelopePrint.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentEnvelopePrint.vue)
- search:
  - [DocumentList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentList.vue)
  - `DOCSEARCH-*` story chain

## Representative-slice Analysis

- Step 1/2 already prove:
  - wizard shell exists
  - batch defaults and row editing exist
  - batch create contract exists
- Existing fee carriers already prove:
  - templates can declare fee-draft behavior
  - backend can auto-create fee drafts and fee items
- Existing carriers do NOT prove:
  - Step 4 applicability inside the wizard
  - Step 4 fee preview contract
  - Step 4 user-adjustment boundary
  - Step 4 final-write timing
  - Step 5 semantics

## Residual Step Semantics Definition

### Applicable draft rows

Step 4 only applies to draft documents where:
- template `fee_draft_type` is non-empty
- and the draft row remains eligible for final document creation

### Candidate generation

For each applicable draft row, Step 4 must define:
- draft type source
- fee item candidate source from `fee_item_list`
- resulting fee preview fields
- whether candidate generation is deterministic and side-effect-free before final submit

### UI contract

Step 4 must freeze which fields are:
- preview-only
- user-adjustable
- derived but overridable

At minimum, the spec must decide the contract for:
- `CaseNo`
- `DocName`
- `FeeDraftType`
- fee item rows
- amount
- currency
- description / item label
- any skip/disable control for one candidate draft

### Final write timing

The spec must explicitly freeze whether:
- Step 4 only previews fee draft candidates in-memory
- or creates temporary side effects before final submit

Current recommended interpretation:
- Step 4 preview stays in-memory
- real `FeeDraft / FeeItem` rows are written only on final wizard completion together with documents

## Step Dependency Options

### Option A — Step 4 consumes stable Step 3

- Freeze Step 4 after Step 3
- Step 4 does not redefine Step 3 timing or applicability
- Recommended

### Option B — Step 4 independently reopens Step 3

- Higher ambiguity
- Not recommended

## First-round Result Shape

- `Step 4 residual contract freeze`
- `narrowed follow-up mapping`

## Deferred Slices Ledger

- Step 5 attachment/template generation
- dispatch / envelope
- document search
- reporting/export
- downstream status transitions
- implementation patching of wizard UI/API/service

## Model-layer Impact

- No schema change is approved in this story
- Only contract interpretation over existing `DocTemplate` / `Document` / `FeeDraft` carriers

## API / Service Impact

- No API or service patch in this story
- But the frozen Step 4 contract must identify which existing fee carriers a future implementation story will consume

## UI / Permission Impact

- No UI patch in this story
- But the frozen contract must state which Step 4 fields future UI may preview or edit

## Cross-module Impact

- `documents`
- `billing`
- explicitly NOT `dispatch / search / reporting`

## SQLite / Phase Compatibility Assessment

- Compatible with current constraints because this is doc-only contract freeze
- If later implementation reveals missing runtime carrier or schema need, work must return to planning

## Risks / Blockers

- Main risk: treating existing backend fee-linking support as if wizard Step 4 were already closed
- Main risk: silently absorbing Step 5 or billing/reporting into the same story
- If the final-submit timing cannot be frozen without discovering new carrier gaps, the story must stop and split a prerequisite

## Exact Closure Slice Candidates

### Preferred slice

- `DOCWIZ-STEP4-SPEC-01`
  - freeze wizard Step 4 fee linkage contract only

### Explicit non-closure

- no Step 5
- no dispatch / envelope
- no search / reporting
- no implementation patch

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a doc-only residual contract freeze for wizard Step 4.
