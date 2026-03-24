# Batch FC3 — Findings

## Backend Dependency (B4)
- CONFIRMED COMPLETE: All 9 dimension columns exist in model + schemas
- Backend enums: CalcMode(FIXED, PER_CLAIM, PER_PAGE, TIER), FeeType(GOV, SERVICE, MISC)

## Discovery: fees.ts mapper gap
- `BackendFeeRate` interface in fees.ts does NOT include dimension fields yet
- `mapFeeRate()` strips them out — must update to pass through
- `toFeeRateCreatePayload()` and `toFeeRateUpdatePayload()` also need updates
- **fees.ts is NOT in the official File Allowlist** but logically required
  - Allowlist says: fees.types.ts, FeeRates.vue, FeeRateForm.vue
  - fees.ts contains the mapper — without updating it, dimension data won't flow to UI
  - **Decision needed**: treat fees.ts as implicitly in scope or flag for user approval

## Additional Findings

### Description field is phantom
- `FeeRate.description` in types is never populated by `mapFeeRate()` — backend `FeeRateOut` has no `description` field.
- The FeeRates.vue table shows a `描述` column that is always empty.
- **Recommendation**: Remove `描述` table column, keep field in types/form for future use.

### Table will be wide
- 8 new columns + existing 5 = 13 columns total. Element Plus auto horizontal scroll handles this.
- Used conservative widths (80-200px) to keep it manageable.

### allow_reduction semantics
- Backend `server_default=text("0")` makes default false.
- Schema type `bool | None` — null means "not set" vs false means "explicitly disabled".
- Form uses el-switch defaulting to false (which matches backend default).

## Bugs Found
(none)
