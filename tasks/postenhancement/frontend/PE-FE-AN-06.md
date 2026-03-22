# PE-FE-AN-06 — Annuity frontend follow-up for task list, pay list, and gov payment closure.

- Source: `tasks/postenhancement/BATCH3_FEES_ANNUITY_MANIFEST_20260317.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the remaining feasible Batch 3 frontend annuity scope.
- Covered items:
  - `US-FE-03`
  - `US-FE-04`
  - `US-FE-05`
  - `FR-FE-04`
  - `FR-FE-05`
  - `FR-FE-06`
- Allowlist:
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
  - `frontend/src/modules/annuity/pages/PayList.vue`
  - `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
  - `frontend/src/modules/annuity/components/InstructionDialog.vue`
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`
- Out of scope:
  - billing pages
  - receipt summary widget
  - unrelated navigation changes
- Acceptance:
  - annuity task list fully exposes instruction, notice, status, and batch draft-generation cues needed by Batch 3
  - pay-list and gov-payment flows expose status/result details required by Batch 3
  - user-facing text remains Simplified Chinese
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement minimal UI + API mapping changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
