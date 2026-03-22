# PE-BE-BL-03 — Billing backend follow-up for prepayment and offset visibility refinement.

- Source: `tasks/postenhancement/BATCH4_BILLING_COLLECTIONS_MANIFEST_20260318.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close one feasible Batch 4 backend prepayment / offset visibility slice.
- Covered items:
  - `US-BL-07`
  - `FR-BL-09`
- Allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/collections/service.py`
  - `backend/tests/test_b5_billing_polish.py`
  - `backend/tests/test_collections_e2e.py`
- Out of scope:
  - dunning generation logic
  - manual bill creation
  - Batch 5 commission effects
- Shared ownership:
  - `Yes`
- Verification:
  - `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/service.py backend/app/modules/collections/service.py backend/tests/test_b5_billing_polish.py backend/tests/test_collections_e2e.py`
  - `cd backend && pytest -q tests/test_b5_billing_polish.py tests/test_collections_e2e.py -k 'offset or payment or receipt'`

## Exact Closure Slice

- This task closes exactly:
  - one backend prepayment / offset visibility or consistency slice inside the existing payment/offset path.

## Explicit Non-Closure Statement

- This task does NOT close:
  - manual bill API contract
  - dunning/bad-debt backend behavior
  - commission settlement consequences

## Remaining Follow-up Task IDs

- `PE-FE-BL-03`

## Done Definition

- [ ] one exact prepayment/offset closure slice implemented
- [ ] no Batch 5 spillover
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-BE-BL-03/baseline_allowlist.diff`
- `artifacts/PE-BE-BL-03/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing test or failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
