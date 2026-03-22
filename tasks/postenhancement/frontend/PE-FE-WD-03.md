# PE-FE-WD-03 — Documents frontend follow-up for defaults and detail cues.

- Source: `tasks/postenhancement/BATCH2_REMAINING_MANIFEST_20260316.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the remaining feasible Batch 2 frontend Documents scope for template defaults, detail cues, and edit parity.
- Covered items:
  - `US-WD-01`
  - `US-WD-02`
  - `US-WD-03`
  - `US-WD-04`
  - `FR-WD-01`
  - `FR-WD-03`
  - `FR-WD-04`
  - `FR-WD-07`
- Allowlist:
  - `frontend/src/modules/documents/pages/DocumentCreate.vue`
  - `frontend/src/modules/documents/pages/DocumentEdit.vue`
  - `frontend/src/modules/documents/pages/DocumentDetail.vue`
  - `frontend/src/modules/documents/pages/DocumentList.vue`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
- Out of scope:
  - document generation
  - new routes
  - unrelated documents redesign
- Acceptance:
  - template default effects are visible in create/edit/detail
  - reply/deadline/fee/status cues are visible in detail/list/create where needed
  - edit page reaches parity with create/detail for Batch 2 fields
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement minimal UI + API mapping changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
