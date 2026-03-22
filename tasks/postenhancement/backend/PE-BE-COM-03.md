# PE-BE-COM-03 — Commission backend follow-up for report completeness refinement.

- Source: `tasks/postenhancement/BATCH5_COMMISSION_CONSULTING_MANIFEST_20260321.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close one feasible Batch 5 backend report completeness slice.
- Covered items:
  - `FR-COM-07`
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
  - `backend/tests/test_commission_e2e.py`
- Out of scope:
  - settlement completion semantics
  - export generation
  - consulting/search logic
- Shared ownership:
  - `Yes`
- Verification:
  - `ruff check backend/app/modules/commission/api.py backend/app/modules/commission/service.py backend/tests/test_commission_e2e.py`
  - `cd backend && pytest -q tests/test_commission_e2e.py -k 'report'`

## Exact Closure Slice

- This task closes exactly:
  - one settlement report completeness refinement on the existing query API, without adding export behavior.

## Explicit Non-Closure Statement

- This task does NOT close:
  - export / print
  - settlement completion marking
  - consulting/search-specific report slices

## Remaining Follow-up Task IDs

- `PE-FE-COM-03`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PE-BE-COM-03/baseline_allowlist.diff`
- `artifacts/PE-BE-COM-03/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing test or failing proof first
- [ ] Implement the minimum fix only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
