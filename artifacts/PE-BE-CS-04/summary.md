# PE-BE-CS-04 Evidence Summary

## Task
- Task ID: `PE-BE-CS-04`
- Task file: `tasks/postenhancement/backend/PE-BE-CS-04.md`
- Scope (allowlist):
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/fees/service.py`

## Implemented
1. Added consulting service interface for CS-05 integration:
   - `generate_consulting_fee_draft(...)` in `consulting/service.py`
   - delegates to fee strategy service.
2. Added fee strategy service:
   - `generate_consulting_fee_draft_strategy(...)` in `fees/service.py`
3. Supported modes:
   - `FIXED`, `HOURLY`, `HYBRID`
4. Deterministic formula + quantization:
   - `amount = round(quantity * unit_price, 2)`
   - monetary fields quantized to 2 decimals
   - quantity normalized deterministically
5. Case scope and mapping:
   - only `case_type in {CONSULTING, SEARCH}`
   - draft type mapping:
     - `CONSULTING -> CONSULT_FEE`
     - `SEARCH -> SEARCH_FEE`
6. Validation and semantics:
   - `404` case not found
   - `400` invalid mode / case type / boundary violations
   - `409` open-draft conflict guard (`case + draft_type + currency + OPEN`)
7. Persistence and totals:
   - persists `FeeDraft` + `FeeItem`
   - runs draft total recompute from persisted lines
   - returns stable output contract:
     - `draft_id`, `draft_type`, `mode`, `currency`, `totals`, `items`, `created_line_count`
8. Traceable line breakdown:
   - each returned line includes:
     - `fee_code`, `fee_name`, `fee_type`, `quantity`, `unit_price`, `amount`, `trace_key`, `remark`

## Verification
- `./scripts/evidence_run.sh PE-BE-CS-04 lint bash -lc 'cd backend && ruff check app/modules/consulting/service.py app/modules/fees/service.py && ruff format --check app/modules/consulting/service.py app/modules/fees/service.py'`
  - `rc=0`
- `./scripts/evidence_run.sh PE-BE-CS-04 test bash -lc 'cd backend && pytest -q'`
  - `rc=0` (`141 passed, 3 warnings`)

## Status Semantics
- `400`: invalid mode/input boundaries/non-consulting case type/numeric violations
- `404`: case not found
- `409`: existing OPEN draft conflict for same case + draft_type + currency

## Evidence Files
- `artifacts/PE-BE-CS-04/results.jsonl`
- `artifacts/PE-BE-CS-04/summary.md`
- `artifacts/PE-BE-CS-04/git/diff.patch`
