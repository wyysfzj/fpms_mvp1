# P2 #19 中间文件专项查询 Strict Query Implementation Ledger Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `query ledger before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Wave | Task ID | Owner | Allowlist | Verification |
|---|---|---|---|---|
| 1 | `DOCSEARCH-LEDGER-01` | main thread | `docs/superpowers/specs/2026-04-06-document-search-implementation-ledger-design.md`, `docs/superpowers/plans/2026-04-06-document-search-implementation-ledger.md`, `tasks/postenhancement/backend/DOCSEARCH-LEDGER-01.md`, `tasks/postenhancement/backend/DOCSEARCH-QA-LEDGER-01.md` | `./scripts/task_validate.sh DOCSEARCH-LEDGER-01` |
| 2 | `DOCSEARCH-QA-LEDGER-01` | main thread | `artifacts/DOCSEARCH-LEDGER-01/**`, `artifacts/DOCSEARCH-QA-LEDGER-01/**`, `tasks/postenhancement/backend/DOCSEARCH-QA-LEDGER-01.md` | `./scripts/task_validate.sh DOCSEARCH-QA-LEDGER-01` |

## Exact Closure Slice

- `DOCSEARCH-LEDGER-01`
  - freeze strict query classification for `#19`
  - freeze `DocType` residual as the first follow-up target

## Explicit Non-closure

- no product implementation
- no review close update
- no dispatch/reply/reporting/export/full-text work

## First Implementation Recommendation

- `DOCSEARCH-DOCTYPE-SPEC-01`

## Deferred

- `DOCSEARCH-EXPORT`
- `DOCSEARCH-FULLTEXT`
- dispatch
- reply workflow
- reporting / print
