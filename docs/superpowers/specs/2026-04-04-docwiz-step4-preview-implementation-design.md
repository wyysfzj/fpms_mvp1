# DOCWIZ-STEP4-IMPL-01 Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE fee-preview implementation before final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`#8 中间文件 5 步向导` 当前已经具备：
- Step 1/2 draft row carrier
- Step 3 preview + final submit integration
- Step 4 fee linkage contract freeze

但 [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue) 中的 Step 4 仍然只是占位。下一轮最自然的实现 slice 不是直接改最终费用写入链，也不是并入 Step 5，而是先将 Step 4 产品化：基于当前 Step 1/2 draft rows 生成费用草稿候选预览，在向导中展示并允许编辑 contract 允许的字段，同时保持候选仅存在于内存态，直到后续 final submit integration 再接入真实写入。

## Assumptions

- 权威对象固定为：
  - `Step 4 preview implementation`
- 结果形态固定为：
  - `frontend Step 4 UI + minimal backend preview support`
- 最小闭环固定为：
  - applicable draft rows only
  - fee candidate preview
  - editable contract fields
  - empty state
  - in-memory only

## Scope

- 在向导中实现 Step 4 预览区
- 显示适用 draft rows 的费用候选
- 支持前端编辑 contract 允许字段
- 无候选时提供空状态

## Explicit Non-scope

- `Step 4 final submit integration`
- `Step 5 product implementation`
- `billing module page enhancements`
- `dispatch/search/reporting/status work`

## Current Implementation Inventory

### Existing wizard shell

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
  - 已有 Step 4 占位
  - 尚无费用候选列表和可调字段 UI

### Existing Step 4 backend carriers

- [fee_linking_service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/fee_linking_service.py)
  - `maybe_create_fee_draft(...)`
  - `_parse_and_create_fee_items(...)`
- [models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/models.py)
  - `DocTemplate.fee_draft_type`
  - `DocTemplate.fee_item_list`

### Existing shared frontend carrier

- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts)
- [documents.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.types.ts)
- Step 2 draft rows already exist inside [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)

## Candidate Field Set

### Primary display fields

- `case_no`
- `source_title` / document title
- `fee_draft_type`
- fee item rows
- `fee_code`
- `fee_name`
- `fee_type`

### First-round editable fields

- `amount`
- `quantity`
- `unit_price`
- `description / item label`
- `skip_this_candidate`

### Deferred fields

- `currency`
- billing assignment / owner semantics
- fee draft status workflow

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
- `BE preview carrier`
- `FE preview wiring`
- `QA close`

It MUST NOT be executed as one mixed atomic task.

## Implementation Recommendation

### Preferred batch

- `DOCWIZ-STEP4-BE-PREVIEW-01`
  - preview-only backend carrier for Step 4 fee candidates
- `DOCWIZ-STEP4-FE-PREVIEW-01`
  - wizard Step 4 UI and editable preview state
- `DOCWIZ-QA-STEP4-IMPL-01`
  - evidence audit and close summary

## SQLite / Phase Compatibility Assessment

- No schema change
- No migration
- Uses existing carriers only
- Compatible with current Phase constraints

## Risks / Blockers

- Main risk: treating final fee draft creation carrier as if Step 4 preview already exists
- Main risk: absorbing Step 4 final submit integration into the same wave
- Main risk: expanding into Step 5 or billing module pages

## Exact Closure Slice Candidates

### Preferred slice family

- `DOCWIZ-STEP4-BE-PREVIEW-01`
- `DOCWIZ-STEP4-FE-PREVIEW-01`
- `DOCWIZ-QA-STEP4-IMPL-01`

### Explicit non-closure

- no Step 4 final submit integration
- no Step 5
- no billing module enhancement
- no dispatch/search/reporting/status work

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- Recommended execution starts with the Step 4 preview wave, not final write integration.
