# `#19` Document Search `DocType` Semantics Freeze

- Date: `2026-04-06`
- Story: `DOCSEARCH-DOCTYPE-SPEC-01`
- Story Shape Classification:
  - `shared_file_density`: `medium`
  - `prereq_dependency_density`: `high`
  - `be_fe_coupling`: `doctype semantics before implementation`
  - `evidence_cost`: `medium`
- `chosen_runbook`: `P0-prereq-heavy-story`

## Problem Statement

`#19 中间文件专项查询` 当前唯一残余缺口是 `DocType`。现有实现把前端 `doc_type` 借道 `ref_no`，而 `SPEC 2.0` 明确要求 `T_Document.DocType` 为独立语义，并支持 `OFFICIAL_IN/OUT/CLIENT_IN/OUT` 查询。

## Current Evidence

- Spec requires:
  - `DocType = OFFICIAL_IN / OFFICIAL_OUT / CLIENT_IN / CLIENT_OUT`
  - query page supports `DocType` multi-select
  - `TemplateCode` is chosen under `DocType`
- Current implementation:
  - `Document.ref_no` exists, `Document.doc_type` does not
  - FE `doc_type` currently maps to `ref_no`
  - create/edit pages write “文档类型” into `ref_no`
  - list page has no independent `DocType` filter

## Semantics Freeze

- `DocType` is an independent document carrier and MUST NOT be aliased to:
  - `direction`
  - `template_code`
  - `ref_no`
- First-round enum authority:
  - `OFFICIAL_IN`
  - `OFFICIAL_OUT`
  - `CLIENT_IN`
  - `CLIENT_OUT`
- `ref_no` remains the reference-number / 文号 carrier.
- Minimal truthful closure for `#19` requires:
  - real `T_Document.DocType` carrier
  - create/update/detail/list API contract support
  - FE create/edit/detail/list user paths
  - multi-select document-search filter

## Prerequisite Decision

`DOCSEARCH-DOCTYPE-01` cannot honestly start from current model state. A prerequisite is required first:

- `DOCSEARCH-DOCTYPE-PRE-DB-01`
  - add `T_Document.DocType`
  - keep SQLite-safe migration
  - do not implement query page in this wave

## Explicit Non-closure

- no dispatch workflow
- no reply workflow implementation changes
- no reporting / export / print / full-text
- no template platform redesign

## Recommended Follow-up Order

1. `DOCSEARCH-DOCTYPE-PRE-DB-01`
2. `DOCSEARCH-DOCTYPE-BE-01`
3. `DOCSEARCH-DOCTYPE-FE-01`
4. `DOCSEARCH-DOCTYPE-QA-01`
5. `DOCSEARCH-CLOSE-01`

