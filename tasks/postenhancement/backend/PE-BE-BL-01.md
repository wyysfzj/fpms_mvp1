# PE-BE-BL-01 — Billing backend follow-up for manual bill contract hardening.

- Source: `tasks/postenhancement/BATCH4_BILLING_COLLECTIONS_MANIFEST_20260318.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the first feasible Batch 4 backend manual-bill slice.
- Covered items:
  - `US-BL-02`
  - `FR-BL-01`
  - `FR-BL-03`
- Allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/tests/test_b5_billing_polish.py`
- Out of scope:
  - bad debt / dunning
  - prepayment / offset
  - bill print/export
  - `Batch 5+`
- Shared ownership:
  - `Yes`
- Verification:
  - `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/service.py backend/app/modules/billing/schemas.py backend/tests/test_b5_billing_polish.py`
  - `cd backend && pytest -q tests/test_b5_billing_polish.py -k 'manual_bill'`

## Exact Closure Slice

- This task closes exactly:
  - `POST /bills/manual` contract hardening for manual AR/AP bill creation with typed payload, explicit item rows, and deterministic total/status initialization.

## Explicit Non-Closure Statement

- This task does NOT close:
  - BillCreate frontend AR/AP and line-editor UI parity
  - bad-debt and dunning behavior
  - prepayment allocation visibility
  - bill detail/list visibility refinements beyond the created response contract

## Remaining Follow-up Task IDs

- `PE-FE-BL-01`
- `PE-BE-BL-02`
- `PE-FE-BL-02`
- `PE-BE-BL-03`
- `PE-FE-BL-03`

## Done Definition

- [ ] `/bills/manual` uses typed schema instead of raw dict payload
- [ ] manual payload supports AR/AP direction and explicit item rows inside current Batch 4 interpretation
- [ ] created bill totals and status are initialized deterministically from the item rows
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-BE-BL-01/baseline_allowlist.diff`
- `artifacts/PE-BE-BL-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing test or failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
