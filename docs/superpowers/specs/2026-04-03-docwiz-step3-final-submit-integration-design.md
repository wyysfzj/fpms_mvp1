# P1 #8 中间文件 5 步向导 Step 3 Final Submit Integration Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE final-submit integration after preview`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

当前 Step 3 preview 已经存在，但最终批量提交链仍然直接从模板默认规则生成任务，没有消费用户在 Step 3 中编辑过的字段。下一轮最自然的实现 slice 不是扩 preview，也不是进入 Step 4/5，而是先完成 `DOCWIZ-STEP3-FINAL-SUBMIT-01`：让 Step 3 preview edits 进入最终 payload，并由后端在创建真实 `T_Task` 时优先使用这些显式值。

## Assumptions

- 权威对象固定为：
  - `Step 3 final-submit integration`
- 结果形态固定为：
  - `shared FE/BE final-submit integration slice`
- 最小闭环固定为：
  - FE submits Step 3 edits
  - BE validates Step 3 task rows
  - explicit values override default generation
  - untouched fields fall back to preview/template-derived values

## Scope

- FE 将 Step 3 编辑值纳入最终 payload
- BE 扩展最终 submit schema 接收 Step 3 任务行
- 最终创建真实任务时优先使用显式字段
- 保持 Step 3 preview 与 final submit 行为一致

## Explicit Non-scope

- Step 4 product implementation
- Step 5 product implementation
- worker/supervisor assignment semantics
- dispatch / search / reporting / downstream status work

## Current Integration Gap

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
  - Step 3 已可编辑 preview fields
  - 最终提交仍只发送 Step 2 payload
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
  - `create_document_wizard_batch(...)` 仍直接调用 `TaskGenerationService().generate_from_document(...)`
  - 不消费 Step 3 显式编辑值
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
  - 当前 final endpoint 只有 `/documents/wizard/batch-create`
  - 推荐扩展现有 endpoint payload，而不是新增第二套 final endpoint

## Shared-file / Ownership Analysis

Serialized frontend ownership files:
- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts)
- [documents.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.types.ts)

Serialized backend ownership files:
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
- [schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/schemas.py)

## Decomposition Recommendation

1. `DOCWIZ-STEP3-BE-FINAL-01`
- extend final submit schema and service wiring
- validate Step 3 task rows
- create real tasks using explicit values first

2. `DOCWIZ-STEP3-FE-FINAL-01`
- include Step 3 edited rows in final payload
- keep preview state aligned with submitted data

3. `DOCWIZ-QA-STEP3-FINAL-01`
- evidence audit and close summary for final-submit integration wave

## Implementation Recommendation

- Reuse existing `/documents/wizard/batch-create`
- Extend payload rather than creating a second finalization endpoint
- Keep task assignment semantics deferred

## SQLite / Phase Compatibility

- No schema change required
- SQLite compatible if integration only extends payload and application-side write behavior

## Risks / Blockers

- Main risk: mixing Step 3 final integration with Step 4/5 payload work
- Main risk: preview state and final payload diverging
- Main risk: silently introducing assignment semantics not frozen in contract

## Exact Closure Slice Candidates

- `DOCWIZ-STEP3-BE-FINAL-01`
  - final submit backend integration only
- `DOCWIZ-STEP3-FE-FINAL-01`
  - final submit frontend payload wiring only
- `DOCWIZ-QA-STEP3-FINAL-01`
  - QA close audit for the final integration wave

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- The implementation must be split into backend final integration, frontend final payload wiring, and QA close tasks.
