# PE-BE-COM-02 — Commission backend follow-up for settlement completion marking.

- Source: `tasks/postenhancement/BATCH5_COMMISSION_CONSULTING_MANIFEST_20260321.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close one feasible Batch 5 backend settlement-completion slice.
- Covered items:
  - `US-COM-06`
  - `FR-COM-06`
- Allowlist:
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/commission/api.py`
  - `backend/tests/test_commission_e2e.py`
- Out of scope:
  - report aggregation redesign
  - new settlement confirmation workflow
  - consulting/search commission rules
- Shared ownership:
  - `Yes`
- Verification:
  - `ruff check backend/app/modules/commission/api.py backend/app/modules/commission/service.py backend/tests/test_commission_e2e.py`
  - `cd backend && pytest -q tests/test_commission_e2e.py -k 'settlement_generate_lines'`

## Exact Closure Slice

- This task closes exactly:
  - settlement line generation updates the related commission rows with deterministic `s1_done / s2_done` completion semantics for the generated settlement amount.

## Explicit Non-Closure Statement

- This task does NOT close:
  - report query completeness
  - frontend settlement UI parity
  - consulting/search-specific settlement behavior

## Remaining Follow-up Task IDs

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

- `artifacts/PE-BE-COM-02/baseline_allowlist.diff`
- `artifacts/PE-BE-COM-02/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing test or failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
