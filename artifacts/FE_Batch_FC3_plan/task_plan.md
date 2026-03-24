# Batch FC3 — Fee Rate Dimensions Display — Task Plan

> Created: 2026-02-27
> Status: Planning

## Objective
Display the new fee rate dimension columns (from backend B4) in the FeeRates page and FeeRateForm.

## Backend Dependency Check
- **Backend B4 Status**: COMPLETE
  - `FeeRate` model has all 9 dimension columns
  - `FeeRateOut` schema exposes all dimension fields
  - `FeeRateCreateIn` / `FeeRateUpdateIn` accept all dimension fields
  - `CalcMode` enum: FIXED | PER_CLAIM | PER_PAGE | TIER

## File Allowlist (STRICT)
| File | Action |
|------|--------|
| `frontend/src/api/fees.types.ts` | MODIFY — add dimension fields to FeeRate type |
| `frontend/src/modules/fees/pages/FeeRates.vue` | MODIFY — add columns to table |
| `frontend/src/modules/fees/components/FeeRateForm.vue` | MODIFY — add dimension fields to form |

**NOTE**: `frontend/src/api/fees.ts` also needs mapping updates (BackendFeeRate → FeeRate mapper must pass through new fields). This file is implicitly required — confirm with user if needed.

## Tasks

### T1: Architect Plan (this document)
- Review all 3 target files + fees.ts mapper
- Confirm backend API contract
- Write detailed execution plan
- **Status**: IN PROGRESS

### T2: Update fees.types.ts
- Add to `FeeRate`: rate_group, country_code, case_type, patent_category, calc_mode, allow_reduction, effective_from, effective_to
- Add to `FeeRateCreatePayload`: same fields
- Add to `FeeRateUpdatePayload`: same fields
- Add `CalcMode` and `RateGroup` union types

### T3: Update fees.ts mapper
- Update `BackendFeeRate` interface with new fields
- Update `mapFeeRate()` to pass through new fields
- Update `toFeeRateCreatePayload()` and `toFeeRateUpdatePayload()` for new fields

### T4: Update FeeRates.vue table
- Add columns: 费率组(rate_group), 计算模式(calc_mode), 生效日期(effective_from/to)
- Optional columns: country_code, case_type, patent_category, allow_reduction

### T5: Update FeeRateForm.vue
- rate_group: el-select (国内/PCT/年费)
- calc_mode: el-select (固定/按权利要求/按页/阶梯) — default FIXED
- effective_from/to: el-date-picker
- allow_reduction: el-switch
- country_code, case_type, patent_category: el-input or el-select

### T6: Quality Gate
- npm run lint && npm run typecheck && npm run build

### T7: Review
- Reviewer checks all changes against acceptance criteria
- Generates review_report.md

## Dependency Graph
```
T1 (Architect) → T2 (types) → T3 (mapper) → T4 (table) + T5 (form) → T6 (QA) → T7 (Review)
```
