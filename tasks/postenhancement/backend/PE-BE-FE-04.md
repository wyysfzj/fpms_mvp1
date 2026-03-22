# PE-BE-FE-04 — Batch 3 backend follow-up for case receipts and fee overview queries.

- Source: `tasks/postenhancement/BATCH3_FEES_ANNUITY_MANIFEST_20260317.md`
- Type: `service + api`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the remaining feasible Batch 3 backend receipt / overview scope without entering Batch 4 billing logic.
- Covered items:
  - `US-FE-06`
  - `US-FE-08`
  - `FR-FE-07`
  - `FR-FE-09`
- Allowlist:
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/fees/service.py`
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/tests/test_annuity_e2e.py`
- Out of scope:
  - dunning
  - bad debt
  - bill offset / reverse offset redesign
  - commission settlement logic
  - `Batch 4+`
- Acceptance:
  - existing receipt data can be queried and displayed with Batch 3 fee-domain semantics
  - fee overview query endpoints or existing endpoints expose the two-list style information required by Batch 3
  - no bill write-path redesign is introduced
- Verification:
  - `ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/tests/test_annuity_e2e.py`
  - `cd backend && pytest -q tests/test_annuity_e2e.py -k 'receipt or overview or pay_list or gov_payment'`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing backend tests first
- [ ] Keep all changes inside Batch 3 read/query/visibility semantics
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
