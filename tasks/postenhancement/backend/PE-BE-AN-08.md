# PE-BE-AN-08 — Annuity backend follow-up for pay-list, gov-payment, and instruction/state closure.

- Source: `tasks/postenhancement/BATCH3_FEES_ANNUITY_MANIFEST_20260317.md`
- Type: `service + api`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the remaining feasible Batch 3 backend annuity chain.
- Covered items:
  - `US-FE-03`
  - `US-FE-04`
  - `US-FE-05`
  - `FR-FE-04`
  - `FR-FE-05`
  - `FR-FE-06`
- Allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
  - `backend/app/modules/tasks/task_generation_service.py`
  - `backend/tests/test_annuity_e2e.py`
- Out of scope:
  - notice-letter generation
  - billing offsets
  - commission consequences
  - `Batch 4+`
- Acceptance:
  - annuity task instruction + notice/status matrix is stable and test-covered
  - annuity draft generation, pay-list creation, and gov-payment registration form a complete non-document-generation chain
  - task generation remains idempotent for covered annuity sources
  - no schema change is introduced
- Verification:
  - `ruff check backend/app/modules/annuity/api.py backend/app/modules/annuity/service.py backend/app/modules/tasks/task_generation_service.py backend/tests/test_annuity_e2e.py`
  - `cd backend && pytest -q tests/test_annuity_e2e.py`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing backend tests first
- [ ] Implement minimum annuity chain fixes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
