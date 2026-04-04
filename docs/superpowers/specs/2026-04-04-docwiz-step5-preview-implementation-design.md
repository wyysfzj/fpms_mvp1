# DOCWIZ-STEP5-IMPL-01 Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE attachment-preview implementation before final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`#8 中间文件 5 步向导` 当前已经具备：
- Step 1/2 draft row carrier
- Step 3 preview + final submit integration
- Step 4 preview + final submit integration
- Step 5 contract freeze

但 [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue) 中的 Step 5 仍然只是占位。下一轮最自然的实现 slice 不是直接改最终附件写入链，也不是并入 dispatch / envelope，而是先将 Step 5 产品化：基于当前 Step 1/2 draft rows 生成附件/模板候选预览，在向导中展示并允许编辑 contract 允许的字段，同时保持候选仅存在于内存态，直到后续 final submit integration 再接入真实附件落库。

## Assumptions

- 权威对象固定为：
  - `Step 5 preview implementation`
- 结果形态固定为：
  - `frontend Step 5 UI + minimal backend preview support`
- 最小闭环固定为：
  - applicable draft rows only
  - attachment/template candidate preview
  - editable contract fields
  - empty state
  - in-memory only

## Scope

- 在向导中实现 Step 5 预览区
- 显示适用 draft rows 的附件/模板候选
- 支持前端编辑 contract 允许字段
- 无候选时提供空状态

## Explicit Non-scope

- `Step 5 final submit integration`
- `dispatch / envelope`
- `document search / reporting / status work`
- `single-document attachment page enhancements`

## Current Implementation Inventory

### Existing wizard shell

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
  - 已有 Step 5 占位
  - 尚无附件/模板候选列表和可调字段 UI

### Existing Step 5-adjacent backend carriers

- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
  - `add_attachment(...)`
  - `get_attachment_download(...)`
- [schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/schemas.py)
  - `DocAttachmentOut`
- [tasks/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/api.py)
  - `DocxRenderer`
  - `render_docx_bytes(...)`

### Existing shared frontend carrier

- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts)
- [documents.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.types.ts)
- Step 2 draft rows already exist inside [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)

## Candidate Field Set

### Primary display fields

- `case_no`
- `source_title` / document title
- `template_code`
- candidate output file name
- output type / format
- candidate source kind

### First-round editable fields

- `output_name`
- `generate_this_candidate`
- `remark`

### Deferred fields

- generated file bytes / blob persistence
- attachment upload workflow
- dispatch / envelope routing semantics

## Shared-file / Ownership Analysis

### Frontend shared files

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
- [documents.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.ts)
- [documents.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/documents.types.ts)

### Backend shared files

- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
- [schemas.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/schemas.py)

### Serialization rule

This story must stay split into:
- `BE preview carrier`
- `FE preview wiring`
- `QA close`

It MUST NOT be executed as one mixed atomic task.

## Implementation Recommendation

### Preferred batch

- `DOCWIZ-STEP5-BE-PREVIEW-01`
  - preview-only backend carrier for Step 5 attachment/template candidates
- `DOCWIZ-STEP5-FE-PREVIEW-01`
  - wizard Step 5 UI and editable preview state
- `DOCWIZ-QA-STEP5-IMPL-01`
  - evidence audit and close summary

## SQLite / Phase Compatibility Assessment

- No schema change
- No migration
- Uses existing carriers only
- Compatible with current Phase constraints

## Risks / Blockers

- Main risk: treating existing single-document attachment carrier as if Step 5 preview already exists
- Main risk: absorbing Step 5 final submit integration into the same wave
- Main risk: expanding into dispatch / envelope or single-document attachment workflow

## Exact Closure Slice Candidates

### Preferred slice family

- `DOCWIZ-STEP5-BE-PREVIEW-01`
- `DOCWIZ-STEP5-FE-PREVIEW-01`
- `DOCWIZ-QA-STEP5-IMPL-01`

### Explicit non-closure

- no Step 5 final submit integration
- no dispatch / envelope
- no search / reporting / status work
- no single-document attachment enhancement

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
- Recommended execution starts with the Step 5 preview wave, not final write integration.
