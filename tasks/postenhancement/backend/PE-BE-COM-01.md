# PE-BE-COM-01 — Commission backend follow-up for manual bill path auto-generation.

- Source: `tasks/postenhancement/BATCH5_COMMISSION_CONSULTING_MANIFEST_20260321.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close one feasible Batch 5 backend commission auto-generation slice.
- Covered items:
  - `US-COM-02`
  - `FR-COM-02`
- Allowlist:
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/commission/service.py`
  - `backend/tests/test_commission_e2e.py`
- Out of scope:
  - payment-state-triggered commission creation
  - settlement completion semantics
  - report aggregation changes
  - consulting/search project-specific attributes
- Shared ownership:
  - `Yes`
- Verification:
  - `ruff check backend/app/modules/billing/service.py backend/app/modules/commission/service.py backend/tests/test_commission_e2e.py`
  - `cd backend && pytest -q tests/test_commission_e2e.py -k 'manual_bill or commission_settlement'`

## Exact Closure Slice

- This task closes exactly:
  - manual bill creation path now triggers the existing commission auto-generation hook and keeps the deterministic upsert behavior.

## Explicit Non-Closure Statement

- This task does NOT close:
  - payment/offset-triggered new commission creation
  - `S1_Done / S2_Done` completion marking
  - commission report completeness
  - consulting/search commission linkage

## Remaining Follow-up Task IDs

- `PE-FE-COM-01`
- `PE-BE-COM-02`
- `PE-FE-COM-02`
- `PE-BE-COM-03`
- `PE-FE-COM-03`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-BE-COM-01/baseline_allowlist.diff`
- `artifacts/PE-BE-COM-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing test or failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
