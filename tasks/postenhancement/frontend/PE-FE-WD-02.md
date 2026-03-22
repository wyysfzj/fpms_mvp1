# PE-FE-WD-02 — Documents frontend completion for Batch 2.

- Source: `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: complete the Batch 2 frontend Documents scope for defaults, reply/deadline cues, fee/status cues, and query capability.
- Covered items:
  - `US-WD-01`
  - `US-WD-02`
  - `US-WD-03`
  - `US-WD-04`
  - `US-WD-06`
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
- Shared ownership files:
  - `frontend/src/modules/documents/pages/DocumentCreate.vue`
  - `frontend/src/modules/documents/pages/DocumentEdit.vue`
  - `frontend/src/modules/documents/pages/DocumentDetail.vue`
  - `frontend/src/modules/documents/pages/DocumentList.vue`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
- Out of scope:
  - `Batch 3+`
  - document generation / printing / envelope / handoff-sheet
  - batch-entry wizard
  - unrelated document module redesign
- Acceptance:
  - create/edit use defaulted fields correctly
  - reply/deadline and fee/status cues are surfaced in Batch 2 scope
  - list/detail support the needed query and view gaps
  - all user-facing text remains Simplified Chinese
- Verification:
  - `npm run lint`
  - `npm run typecheck`
  - manual notes for create / edit / detail / list in Batch 2 scope

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal validation-first step
- [ ] Implement minimal UI + API mapping changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
