# P1 #8 中间文件 5 步向导 Step 3 Deadline Linkage Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared multi-lane residual contract before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`P1 #8 中间文件 5 步向导` 当前已经具备 Step 1/2 representative slices，但 full 5-step closure 仍未成立。对于 residual program 的第一轮收口，当前最自然的 closure 不是继续扩页面，而是先冻结 `Step 3 – 生成相关时限任务` 的 contract：哪些待创建 document 会进入 Step 3、Step 3 需要展示和允许调整哪些任务字段、以及这些任务在“完成向导”时如何与 document 创建统一落库。

## Assumptions

- 权威对象固定为：
  - `wizard Step 3 deadline linkage semantics`
- Step 1/2 已有实现不自动等于 full 5-step closure
- dispatch / envelope / search 不自动等于 wizard closure
- 第一轮 residual choice 固定为：
  - `Step 3 deadline linkage`
- 第一轮结果形态固定为：
  - `residual design / contract freeze`
- 第一轮最小闭环固定为：
  - one step contract
  - one step linkage semantics
  - one explicit deferred ledger

## Scope

- 冻结 Step 3 的适用条件
- 冻结 Step 3 的 task candidate 生成语义
- 冻结 Step 3 UI 需展示/可调整字段的 contract
- 冻结 Step 3 与“最终完成向导”之间的写入关系

## Explicit Non-scope

- Step 4 fee linkage
- Step 5 attachments/template generation
- dispatch / envelope
- document search
- reporting/export
- 任何 frontend/backend 实现补丁

## Current Page / API / Service Inventory

### Existing wizard shell and Step 1/2 slices

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
- [documents/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
  - `POST /documents/wizard/batch-create`
- [documents/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
  - `create_document_wizard_batch(...)`

### Existing Step 3 backend carriers

- [documents/models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/models.py)
  - `DocTemplate.deadline_template_code`
  - `Document.need_reply`
- [tasks/task_generation_service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/task_generation_service.py)
  - task template resolution
  - deadline base resolution
  - due/reminder generation support

### Existing surrounding document capabilities that are NOT wizard closure

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
- Step 1/2 do NOT prove:
  - Step 3 task candidate projection
  - Step 3 field-adjustment boundary
  - Step 3 final-write timing
  - Step 4 / Step 5 semantics

## Residual Step Semantics Definition

### Applicable draft rows

Step 3 only applies to draft documents where:
- template `deadline_template_code` is non-empty
- and the draft row requires reply or otherwise satisfies the template’s task-generation condition

### Candidate generation

For each applicable draft row, Step 3 must define:
- BaseDate source
- TaskTemplate lookup source
- resulting task fields to preview
- whether candidate generation is deterministic and side-effect-free before final submit

### UI contract

Step 3 must freeze which fields are:
- preview-only
- user-adjustable
- derived but overridable

At minimum, the spec must decide the contract for:
- `CaseNo`
- `DocName`
- `TaskTemplateCode / Task Type`
- `BaseDate`
- `Deadline`
- `InnerDeadline`
- `Worker`
- `Supervisor`
- reminder dates

### Final write timing

The spec must explicitly freeze whether:
- Step 3 only previews candidates in-memory
- or creates temporary side effects before final submit

Current recommended interpretation:
- Step 3 preview stays in-memory
- real `T_Task` rows are written only on final wizard completion together with documents

## Step Dependency Options

### Option A — Step 3 precedes Step 4

- Freeze Step 3 first
- Step 4 consumes already-stable wizard/document contract afterward
- Recommended

### Option B — Step 3 and Step 4 are parallel

- Possible only if the final-submit contract is proven independent
- Currently higher ambiguity

## First-round Result Shape

- `Step 3 residual contract freeze`
- `narrowed follow-up mapping`

## Deferred Slices Ledger

- Step 4 fee linkage
- Step 5 attachment/template generation
- dispatch / envelope
- document search
- reporting/export
- downstream status transitions
- implementation patching of wizard UI/API/service

## Model-layer Impact

- No schema change is approved in this story
- Only contract interpretation over existing `DocTemplate` / `Document` / `TaskTemplate` carriers

## API / Service Impact

- No API or service patch in this story
- But the frozen Step 3 contract must identify which existing backend carriers a future implementation story will consume

## UI / Permission Impact

- No UI patch in this story
- But the frozen contract must state which Step 3 fields future UI may preview or edit

## Cross-module Impact

- `documents`
- `tasks`
- explicitly NOT `dispatch / search / reporting`

## SQLite / Phase Compatibility Assessment

- Compatible with current constraints because this is doc-only contract freeze
- If later implementation reveals missing runtime carrier or schema need, work must return to planning

## Risks / Blockers

- Main risk: treating existing backend task-generation support as if wizard Step 3 were already closed
- Main risk: silently absorbing Step 4 or dispatch/search into the same story
- If the final-submit timing cannot be frozen without discovering new carrier gaps, the story must stop and split a prerequisite

## Exact Closure Slice Candidates

### Preferred slice

- `DOCWIZ-STEP3-SPEC-01`
  - freeze wizard Step 3 deadline linkage contract only

### Explicit non-closure

- no Step 4
- no later steps
- no dispatch / envelope
- no search / reporting
- no implementation patch

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The atomic task is a doc-only residual contract freeze for wizard Step 3.
