# Wave 36 Final Independent Review Report

Date: 2026-02-28  
Role: Reviewer (Wave 36)  
Scope: `PE-BE-CS-04`

## Inputs Reviewed
- `artifacts/postenhancement/wave-36/task_plan.md`
- `artifacts/postenhancement/wave-36/contracts/contract_freeze.md`
- `artifacts/postenhancement/wave-36/test_report.md`
- `artifacts/postenhancement/wave-36/progress.md`
- `artifacts/postenhancement/wave-36/findings.md`
- `artifacts/PE-BE-CS-04/**`

## Findings (Ordered by Severity)
1. INFO - No unresolved blockers for `PE-BE-CS-04`.
   - Allowlist scope is respected (`consulting/service.py` + `fees/service.py` only).
   - Strategy modes `FIXED/HOURLY/HYBRID` are implemented with deterministic formulas and rounding.
   - Line breakdown is traceable and service output interface is stable for `CS-05`.
   - Boundary validations and `400/404/409` semantics are implemented.
   - Independent task gate and full pytest re-run pass.

## Checklist Verification

### 1) Allowlist compliance (`consulting/service.py` + `fees/service.py` only)
- PASS
- Evidence:
  - `artifacts/PE-BE-CS-04/git/diff.patch` modifies only:
    - `backend/app/modules/consulting/service.py`
    - `backend/app/modules/fees/service.py`
  - `./scripts/task_validate.sh PE-BE-CS-04` -> `Task Gate PASS`

### 2) Strategy modes + deterministic formulas
- PASS
- Evidence in `backend/app/modules/fees/service.py`:
  - mode gate supports exactly `FIXED`, `HOURLY`, `HYBRID`.
  - deterministic amount computation:
    - hourly/misc line amounts quantized via `_quantize_money`
    - quantity quantized via `_quantize_quantity`
    - formulas consistently compute `amount = quantity * unit_price` (with mode-specific constraints)
  - mode-specific boundaries:
    - `FIXED`: `fixed_fee > 0`
    - `HOURLY`: required hourly lines, `hours > 0`, `hourly_rate >= 0`
    - `HYBRID`: `fixed_fee >= 0`, hourly lines required, total must be `> 0`

### 3) Traceable line breakdown + stable interface for CS-05
- PASS
- Evidence:
  - each generated line carries trace fields:
    - `fee_code`, `fee_name`, `fee_type`, `quantity`, `unit_price`, `amount`, `trace_key`, `remark`
  - remarks include deterministic trace markers (`mode=...;trace_key=...;source=...`).
  - service return contract is stable and integration-friendly:
    - `draft_id`, `draft_type`, `mode`, `currency`, `totals`, `items`, `created_line_count`
  - consulting facade in `consulting/service.py` (`generate_consulting_fee_draft(...)`) delegates cleanly to strategy service for CS-05 reuse.

### 4) Boundary validations + `400/404/409` semantics
- PASS
- Evidence in `backend/app/modules/fees/service.py`:
  - `404`: case not found (`CASE_NOT_FOUND`).
  - `400`: invalid mode, invalid case type, invalid currency, invalid numeric boundaries, and malformed line payloads (`CONSULTING_FEE_INVALID`).
  - `409`: conflict guard when existing OPEN draft for same `case + draft_type + currency` (`FEE_DRAFT_CONFLICT`).

## Independent Gate + Pytest Re-run
- `./scripts/task_validate.sh PE-BE-CS-04` -> PASS
- `cd backend && pytest -q` -> PASS (`141 passed, 3 warnings in 30.83s`)

## Verdict
- `PE-BE-CS-04`: ACCEPT
- Wave 36 reviewer sign-off: PASS
