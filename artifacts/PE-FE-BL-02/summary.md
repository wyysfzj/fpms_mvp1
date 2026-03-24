# PE-FE-BL-02

Status: PASS

Atomic Task File:
- `tasks/postenhancement/frontend/PE-FE-BL-02.md`

Covered Items:
- `US-BL-06`
- `FR-BL-07`
- `FR-BL-08`

Exact Closure Slice:
- Dunning detail view now calls `GET /dunning/{id}` and renders the returned batch head, summary counts, and `DunningLine` rows; no other frontend page is touched.

Explicit Non-Closure:
- does not adjust `DunningList`, `DunningCreate`, or any collection list filters beyond the existing allowlist content
- does not introduce prepayment/offset views, manual bill updates, or document generation
- does not implicitly absorb broader scaffolded billing API or list UX diffs that existed before this task (baseline recorded in `artifacts/PE-FE-BL-02/baseline_allowlist.diff`)

Incremental Implementation:
- `frontend/src/api/collections.ts`: added `DunningDetail` mapping plus `getDunningDetail` client for the new endpoint and enriched types for the returned lines/summary.
- `frontend/src/api/collections.types.ts`: introduced `DunningDetail`/`DunningDetailLine` type definitions to match the backend contract.
- `frontend/src/modules/collections/pages/DunningDetail.vue`: refocused the page to load one batch detail via the new client, kept navigation/query states, and rendered the returned lines/summary counts.

Dirty Baseline Handling:
- allowlist files started with wider billing/collections diffs; this task only scopes the new detail view delta after `baseline_allowlist.diff`, leaving historical changes out of scope.
- baseline external files list documents the rest of the dirty worktree for audit.

Validation:
- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`

Notes:
- no Batch 5 spillover
- no document generation work
- exact closure slice only
