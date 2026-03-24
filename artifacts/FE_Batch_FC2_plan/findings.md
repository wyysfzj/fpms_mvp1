# FC2 Batch — Findings

## Backend Dependency Check
- Backend B2 Document Reply Chain: **VERIFIED** — reply_to_id, need_reply, reply_date present in model, schemas, API
- Backend B1 DocTemplate: **VERIFIED** — GET /doc-templates with pagination, need_reply field present

## Bugs Found
1. **Duplicate `case_no` in Document interface** — Agent added case_no at line 21 when it already existed at line 10. Caught by typecheck (`TS2300: Duplicate identifier`). Fixed by removing the duplicate.
2. **Pre-existing: `case_no` dropped by `mapDocument()`** — Backend returns case_no but old mapDocument() didn't forward it. Fixed as part of T0 scope deviation.

## Deviations
1. **SD1: `documents.ts` added as file #5** — Not in original 4-file allowlist. Required because BackendDocument interface and mapDocument() silently drop all reply chain fields, making FC2 impossible without the fix. Same pattern as FB3 (cases.ts). Approved by team lead.
2. **Reviewer agent stalled** — Review report written by team lead as fallback after reviewer agent failed to produce output.
