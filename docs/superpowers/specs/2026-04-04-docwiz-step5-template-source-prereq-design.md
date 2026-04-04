# DOCWIZ-STEP5-PREREQ-01 Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared prerequisite freeze before Step 5 final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`DOCWIZ-STEP5-FINAL-SUBMIT-01` 的目标是让向导 Step 5 preview 中确认过的附件/模板候选在最终完成向导时真正写入 `T_DocAttachment`。但当前 repo 尚未具备一个可直接消费的模板来源映射：

- [DocTemplate](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/models.py)
  - 只有 `code / name / direction / input_fields`
  - 没有模板文件路径字段
- [Template](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/templates/models.py)
  - 有 `file_path`
  - 但当前与 `DocTemplate` 没有现成关系或解析契约
- [DocAttachment](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/models.py)
  - 不是纯元数据
  - 需要真实 `file_path`

因此当前缺的不是 Step 5 最终提交的 FE/BE 接线，而是一个前置 prerequisite：
- `DocTemplate` 如何解析到真实模板文件来源
- 以及最终生成附件时使用哪条渲染/持久化链

## Assumptions

- 权威对象固定为：
  - `Step 5 template source mapping prerequisite`
- 当前结果形态固定为：
  - `doc-only prerequisite freeze`
- 当前最小闭环固定为：
  - confirm blocker
  - freeze source-mapping options
  - freeze deferred final-submit scope
  - produce next-task recommendation

## Scope

- 明确 Step 5 final submit 当前为何不可直接实现
- 冻结 `DocTemplate -> render source` 的 prerequisite 需求
- 冻结后续真正实现必须依赖的 source-mapping contract

## Explicit Non-scope

- 不做任何产品实现补丁
- 不修改 `DocTemplate` / `Template` schema
- 不实现 Step 5 final submit integration
- 不扩展 dispatch / envelope / reporting

## Current Evidence

### Existing Step 5 preview

- [DocumentWizard.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/documents/pages/DocumentWizard.vue)
- [api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/api.py)
  - `POST /documents/wizard/attachment-preview`
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
  - `preview_document_wizard_attachment_candidates(...)`

### Existing attachment persistence carrier

- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/service.py)
  - `add_attachment(...)`
- [models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/documents/models.py)
  - `DocAttachment.file_path`

### Existing render carrier outside documents wizard

- [renderer.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/common/doc_render/renderer.py)
- [tasks/api.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/tasks/api.py)
  - uses `SystemParam.task_sheet_template_path`

### Existing generic template registry

- [models.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/templates/models.py)
  - `Template.file_path`
- [service.py](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/app/modules/templates/service.py)

## Blocker Statement

Current blocker is concrete:

- Step 5 final submit needs a real template source path in order to render bytes or generate attachment files.
- `DocTemplate` does not currently expose any field or service contract that resolves to a renderable file path.
- No existing wizard/service contract defines how `DocTemplate.code` maps to `Template.file_path`.

Without that mapping, Step 5 final submit would have to:
- guess a file path
- invent an implicit code convention
- or write attachment metadata without a real file

All three are outside the approved contract.

## Source-mapping Options

### Option A — Add explicit mapping from `DocTemplate` to `Template`

- Most direct
- But likely requires schema/API work
- Must be planned as a prerequisite task, not absorbed into Step 5 final submit

### Option B — Freeze a deterministic code-based resolver

- Lower immediate write surface
- But only valid if the repo already has a stable naming convention and storage layout
- Current evidence does not show such a stable contract

### Option C — Reuse `SystemParam`-style template path configuration

- Consistent with current task-sheet rendering
- But still requires a new explicit contract for document wizard templates

## Recommended Conclusion

- `DOCWIZ-STEP5-FINAL-SUBMIT-01` is currently **not implementation-ready**
- A new prerequisite task must first freeze template source mapping

## Exact Closure Slice

- `DOCWIZ-STEP5-PREREQ-01`
  - freeze Step 5 template source mapping blocker and next prerequisite recommendation only

## Explicit Non-closure

- no schema change
- no API/service implementation
- no final attachment write integration

## Design Conclusion

- `不可直接实现，必须先新增 prerequisite task(s)`
