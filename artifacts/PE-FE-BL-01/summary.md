# PE-FE-BL-01

Status: PASS

Atomic Task File:
- `tasks/postenhancement/frontend/PE-FE-BL-01.md`

Covered Items:
- `US-BL-02`
- `FR-BL-01`
- `FR-BL-03`

Exact Closure Slice:
- `BillCreate` manual-bill mode parity for AR/AP direction selection and explicit item-row payload mapping to the hardened `/bills/manual` backend contract.

Explicit Non-Closure:
- does not close bad-debt or dunning UI
- does not close prepayment or offset visibility
- does not close bill detail/list redesign
- does not close the broader draft-mode selector enhancement already present in the allowlist baseline

Incremental Implementation:
- `frontend/src/modules/billing/pages/BillCreate.vue`: added manual-bill direction selector in the form and wired `manualForm.direction` into the create payload.

Dirty Baseline Handling:
- allowlist files already had pre-existing dirty diffs before this task began, including broader billing API/detail typing changes and draft-mode UX changes.
- acceptance for this task is scoped only to the manual-bill direction/payload delta recorded after `artifacts/PE-FE-BL-01/baseline_allowlist.diff`.
- broader `billing.ts`, `billing.types.ts`, and draft-mode changes are not counted toward this task closure.

Validation:
- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`

Notes:
- no Batch 5 spillover
- no document generation behavior added
- no bill detail/list or collections page redesign
- this is one frontend closure slice only
