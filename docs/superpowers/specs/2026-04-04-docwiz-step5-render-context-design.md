# DOCWIZ-STEP5-RENDER-CONTEXT-01 Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `backend prerequisite implementation before Step 5 final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`DOCWIZ-STEP5-FINAL-SUBMIT-01` 现在已经具备：

- template source resolver
- generated attachment persistence helper

但 documents 模块仍缺一个可复用的 render-context contract。没有这条 helper，final submit 就必须在同一个故事里同时回答：

- 用哪些 `Document` 字段
- 用哪些 `Case` 字段
- 用哪些 `Client` 字段
- `extra_data` 如何暴露给模板

这会让 final-submit integration 再次吸收新的 service closure slice。

## Assumptions

- 权威对象固定为：
  - `document template render-context helper`
- 当前不改 schema
- 当前不改 API
- 当前不改前端

## Scope

- 为 documents 模块实现模板渲染 context helper
- 冻结最小字段集
- 补 targeted backend tests

## Explicit Non-scope

- 不做 Step 5 final submit integration
- 不调用模板渲染
- 不做附件落库
- 不改前端

## Context Contract

- top-level:
  - `document_id`
  - `document_title`
  - `document_direction`
  - `document_date`
  - `document_ref_no`
  - `document_extra_data`
  - `template_code`
- nested `case`:
  - `id`
  - `case_no`
  - `title`
  - `title_cn`
  - `title_en`
  - `app_no`
- nested `client`:
  - `id`
  - `name`
  - `name_cn`
  - `name_en`
- nested `document` mirror object for template ergonomics

## Exact Closure Slice

- `DOCWIZ-STEP5-RENDER-CONTEXT-01`
  - implement documents-side render-context helper only

## Explicit Non-closure

- no renderer invocation
- no attachment persistence
- no final submit integration

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
