# PE-FE-AN-06

Status: PASS

Scope:
- `frontend/src/api/annuity.ts`

Changes:
- added frontend-side currency normalization before calling `/annuity/tasks/generate-drafts`
- normalized user-provided currency to uppercase with fallback `CNY`
- aligned frontend request behavior with the Batch 3 backend annuity currency-normalization slice

Validation:
- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`

Notes:
- no route changes
- no billing UI spillover
- no document generation behavior added
- existing annuity page label changes were treated as dirty baseline and were not counted toward this task
