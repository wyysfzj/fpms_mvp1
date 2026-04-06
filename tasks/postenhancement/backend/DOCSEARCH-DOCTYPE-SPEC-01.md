# DOCSEARCH-DOCTYPE-SPEC-01 — document search doctype semantics freeze

- Source: `docs/superpowers/plans/2026-04-06-document-search-doctype-semantics.md`
- Type: `spec / prerequisite decision`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 `#19` 中 `DocType` 的独立语义，并判断是否必须先做 carrier prerequisite。
- Exact closure slice:
  - 明确 `DocType` 不能继续映射到 `ref_no`
  - 明确最小 truthful closure 需要真实 `T_Document.DocType`
  - 明确 follow-up 必须先进入 `DOCSEARCH-DOCTYPE-PRE-DB-01`
- Explicit non-closure:
  - 不做任何产品实现
  - 不更新 `#19` close decision
- Remaining follow-up task ids:
  - `DOCSEARCH-DOCTYPE-PRE-DB-01`
  - `DOCSEARCH-QA-DOCTYPE-SPEC-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-06-document-search-doctype-semantics-design.md`
  - `docs/superpowers/plans/2026-04-06-document-search-doctype-semantics.md`
  - `tasks/postenhancement/backend/DOCSEARCH-DOCTYPE-SPEC-01.md`
  - `tasks/postenhancement/backend/DOCSEARCH-QA-DOCTYPE-SPEC-01.md`
- Verification:
  - `./scripts/task_validate.sh DOCSEARCH-DOCTYPE-SPEC-01`

## Execution Checklist

- [x] Freeze `DocType` as independent carrier semantics
- [x] Freeze `ref_no` as non-equivalent reference-number carrier
- [x] Record `DOCSEARCH-DOCTYPE-PRE-DB-01` as mandatory next story
