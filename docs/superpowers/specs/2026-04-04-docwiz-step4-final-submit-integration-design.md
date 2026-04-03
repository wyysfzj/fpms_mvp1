# DOCWIZ-STEP4-FINAL-SUBMIT-01 Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE final-submit integration after Step 4 preview`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

当前 Step 4 preview 已经存在，但最终批量提交链仍然直接从模板默认规则创建费用草稿，没有消费用户在 Step 4 中编辑过的字段。下一轮最自然的实现 slice 不是扩 preview，也不是进入 Step 5，而是先完成 `DOCWIZ-STEP4-FINAL-SUBMIT-01`：让 Step 4 preview edits 进入最终 payload，并由后端在创建真实 `FeeDraft / FeeItem` 时优先使用这些显式值。

## Assumptions

- 权威对象固定为：
  - `Step 4 final-submit integration`
- 结果形态固定为：
  - `shared FE/BE final-submit integration slice`
- 最小闭环固定为：
  - FE submits Step 4 edits
  - BE validates Step 4 fee rows
  - explicit values override default fee generation
  - fallback to preview/template-derived values for untouched fields

## Scope

- FE 提交 Step 4 费用编辑值
- BE 接收并校验 Step 4 费用行
- 最终写入真实 `FeeDraft / FeeItem` 时消费显式值
- 保持 Step 4 preview 语义与最终提交一致

## Explicit Non-scope

- `Step 5 product implementation`
- `billing module page enhancements`
- `fee draft downstream workflow semantics`
- `dispatch/search/reporting/status work`

## Current Integration Gap

### Frontend gap

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue) 中 Step 4 preview edits 目前只存在于内存态
- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts) 的最终提交 payload 目前没有 `fee_rows`

### Backend gap

- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
  - `create_document_wizard_batch(...)` 仍直接 `maybe_create_fee_draft(...)`
  - 不会消费 Step 4 preview 的显式编辑值
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
  - `/documents/wizard/batch-create` 尚未承载 Step 4 final rows schema

## Shared-file / Ownership Analysis

### Frontend shared files

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts)
- [documents.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.types.ts)

### Backend shared files

- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
- [schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/schemas.py)
- [fee_linking_service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/fee_linking_service.py)

### Serialization rule

This story must stay split into:
- `BE final-submit carrier`
- `FE final payload wiring`
- `QA close`

It MUST NOT be executed as one mixed atomic task.

## Implementation Recommendation

### Preferred batch

- `DOCWIZ-STEP4-BE-FINAL-01`
  - extend final submit schema and backend write path for Step 4 fee rows
- `DOCWIZ-STEP4-FE-FINAL-01`
  - include Step 4 edits in final payload
- `DOCWIZ-QA-STEP4-FINAL-01`
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

- Main risk: silently ignoring Step 4 preview edits and leaving them product-ineffective
- Main risk: absorbing Step 5 or billing workflow into the same wave
- Main risk: forking a second final submit endpoint and splitting wizard finalization semantics

## Exact Closure Slice Candidates

### Preferred slice family

- `DOCWIZ-STEP4-BE-FINAL-01`
- `DOCWIZ-STEP4-FE-FINAL-01`
- `DOCWIZ-QA-STEP4-FINAL-01`

### Explicit non-closure

- no Step 5
- no billing page enhancement
- no downstream fee workflow semantics
- no dispatch/search/reporting/status work

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- Recommended execution starts with Step 4 final-submit integration, not Step 5.
