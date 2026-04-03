# P1 #8 中间文件 5 步向导 Step 3 Preview Implementation Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared preview implementation before final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`#8` 当前已经具备 5-step shell，也已经冻结了 Step 3 deadline linkage contract，但 Step 3 仍只是占位。下一轮实现不应直接改最终 batch-create 写入链，而应先把 Step 3 产品化：基于 Step 1/2 的 draft rows 生成任务候选预览，在向导中展示并允许编辑 contract 允许的字段，同时保持所有候选仅存在于内存态，直到后续 final submit integration 再接入真实写入。

## Assumptions

- 权威对象固定为：
  - `Step 3 preview implementation`
- 结果形态固定为：
  - `frontend Step 3 UI + minimal backend preview support`
- 最小闭环固定为：
  - applicable draft rows only
  - task candidate preview
  - editable contract fields
  - empty state
  - in-memory only

## Scope

- 增加 Step 3 预览 carrier
- 基于 Step 1/2 draft rows 计算任务候选
- 在向导中展示候选任务
- 允许编辑 contract 允许的字段
- 无候选时提供空状态

## Explicit Non-scope

- Step 3 final submit integration
- Step 4 product implementation
- Step 5 product implementation
- dispatch / search / reporting / downstream status work

## Current Implementation Inventory

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
  - 已有 5-step shell
  - Step 3 仍是纯占位
- [task_generation_service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/task_generation_service.py)
  - 已有任务生成 carrier
  - 当前面向真实写入，不提供 preview candidate API
- [documents.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.types.ts)
  - wizard state 目前只有 Step 1 carrier
  - 无 Step 2 shared draft rows / Step 3 preview candidates

## Candidate Field Set

### Preview/display fields

- `case_no`
- `source_title / doc title`
- `task template code / task title`
- `base_date`
- `due_date`
- `internal_due_date`
- `remind1`
- `remind2`
- `remind3`
- `daily_remind_from`

### Editable fields for first implementation slice

- `title`
- `internal_due_date`
- `remind1`
- `remind2`
- `remind3`

### Explicitly deferred in this slice

- `worker`
- `supervisor`
- assignment semantics

## Shared-file / Ownership Analysis

Serialized frontend ownership files:
- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts)
- [documents.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.types.ts)

Serialized backend ownership files:
- [documents/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
- [documents/service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
- [documents/schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/schemas.py)

## Decomposition Recommendation

1. `DOCWIZ-STEP3-BE-PREVIEW-01`
- add minimal preview endpoint/service/schema carrier
- no final write integration

2. `DOCWIZ-STEP3-FE-PREVIEW-01`
- consume preview carrier in wizard Step 3
- render candidate list, editable fields, and empty state

3. `DOCWIZ-QA-STEP3-IMPL-01`
- evidence audit and close summary for the preview wave

## SQLite / Phase Compatibility

- No schema change required
- SQLite compatible if preview support stays read/compute only
- If implementation reveals a missing runtime carrier that requires schema work, stop and split a prerequisite

## Risks / Blockers

- Main risk: accidentally mixing preview with final write integration
- Main risk: silently absorbing Step 4 fields into Step 3 preview
- Main risk: over-expanding editable fields to worker/supervisor assignment

## Exact Closure Slice Candidates

- `DOCWIZ-STEP3-BE-PREVIEW-01`
  - preview-only backend carrier
- `DOCWIZ-STEP3-FE-PREVIEW-01`
  - preview-only Step 3 UI
- `DOCWIZ-QA-STEP3-IMPL-01`
  - QA close audit for this preview wave

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The implementation must be split into backend preview, frontend preview, and QA close tasks.
