# PE-FE-CM-03 — Cases UI completion for foreign agent, PCT, invalidation, and bio deposit.

- Source: `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: complete deferred Batch 1 frontend behavior for foreign agent / PCT / invalidation / bio deposit.
- Covered items:
  - `FR-CM-03`
  - `FR-CM-05`
- Allowlist:
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/api/clients.ts`
- Shared ownership files:
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/api/clients.ts`
- Out of scope:
  - Batch 2+ scope
  - client masterdata redesign outside minimal quick-create support
  - document generation
- Acceptance:
  - create/edit support foreign-agent select + quick-create + backfill
  - create/edit support bio-deposit rows
  - create/edit support PCT and invalidation conditional sections
  - detail page shows all deferred Batch 1 fields
- Verification:
  - `npm run lint`
  - `npm run typecheck`
  - manual case create / edit / detail notes for deferred fields

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal validation-first step
- [ ] Implement minimal UI + API mapping changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
