# FC3 Review Report — Fee Rate Dimensions Display

> Reviewer Agent | Date: 2026-02-27

## Overall Verdict
**PASS WITH NOTES**

All 8 acceptance criteria are satisfied. The implementation faithfully follows the architect plan. Three minor observations are noted below for awareness but none are blocking.

---

## Acceptance Criteria Checklist

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | FeeRate type includes all 9 B4 dimension fields | **PASS** | `rate_group`, `country_code`, `case_type`, `patent_category`, `calc_mode`, `calc_params`, `allow_reduction`, `effective_from`, `effective_to` all present in `FeeRate`, `FeeRateCreatePayload`, `FeeRateUpdatePayload` |
| 2 | API mapper passes dimension fields (no data loss) | **PASS** | `mapFeeRate()` maps all 9 fields using `?? null` for consistent nullability. `BackendFeeRate` interface matches `FeeRateOut` schema. |
| 3 | Create/Update payloads send dimension fields to backend | **PASS** | `toFeeRateCreatePayload` conditionally spreads all 9 fields. `toFeeRateUpdatePayload` conditionally assigns all 9 fields. |
| 4 | Table displays: 费率组, 计算模式, 案件类型, 专利类别, 国家/地区, 允许减缴, 有效期 | **PASS** | All 7 required columns present, plus bonus 费用类型 column. Old empty 描述 column removed. |
| 5 | Form allows setting all dimension fields with appropriate components | **PASS** | el-select for rate_group/calc_mode/case_type/patent_category; el-input for country_code; el-switch for allow_reduction; el-date-picker for dates; el-input textarea for calc_params |
| 6 | Edit mode pre-fills all dimension fields | **PASS** | `watch(() => props.rate, ...)` handler sets all 9 fields with `?? null` (or `?? false` for allow_reduction) |
| 7 | Quality gate passes: lint + typecheck + build | **PASS** | Confirmed in progress.md: lint (0 warnings), typecheck (pass), build (3.23s) |
| 8 | All labels in 简体中文 | **PASS** | No English user-facing text found. All labels, placeholders, messages, empty states, and el-option labels are in Chinese. |

---

## Code Quality Checks

| Check | Status | Notes |
|-------|--------|-------|
| No `@/` import aliases | **PASS** | All 4 files use relative imports (`../../../api/fees`, etc.) |
| No inline hex colors | **PASS** | FeeRates.vue uses `var(--font-mono)`; FeeRateForm.vue has no color declarations |
| All el-select have `clearable` prop | **PASS** | rate_group, calc_mode, case_type, patent_category all have `clearable`. Currency select correctly omits `clearable` (required field). |
| Dialog width updated | **PASS** | Changed to `680px` to accommodate dimension fields section |
| `resetForm()` clears all new fields | **PASS** | All 9 dimension fields reset; `allow_reduction` resets to `false` (not null) |
| `handleSubmit()` includes all fields | **PASS** | Payload object includes all 9 dimension fields |
| Label helpers correct Chinese | **PASS** | 5 label functions verified: `feeTypeLabel`, `rateGroupLabel`, `calcModeLabel`, `caseTypeLabel`, `patentCategoryLabel` — all translations match architect plan |
| `CalcMode` union type correct | **PASS** | `'FIXED' \| 'PER_CLAIM' \| 'PER_PAGE' \| 'TIER'` matches backend `CalcMode` enum exactly |
| `RateGroup` union type correct | **PASS** | `'DOMESTIC' \| 'PCT' \| 'ANNUITY'` matches backend convention |
| `BackendFeeRate` matches `FeeRateOut` | **PASS** | All fields present with correct types (JS equivalents of Python types) |
| No files outside allowlist modified | **PASS** | Only fees.types.ts, fees.ts, FeeRates.vue, FeeRateForm.vue were touched (fees.ts was flagged as critically needed in architect plan) |
| `allow_reduction` defaults to `false` | **PASS** | Form init: `false`; resetForm: `false`; watch handler: `?? false` |
| Date picker `value-format="YYYY-MM-DD"` | **PASS** | Both `effective_from` and `effective_to` date pickers use `value-format="YYYY-MM-DD"` |
| Empty 描述 column removed | **PASS** | Column removed from table; description field still in form for user notes |

---

## Issues Found

### Minor (Non-blocking)

1. **`RateGroup` type exported but never used**
   - `fees.types.ts:6` defines `export type RateGroup = 'DOMESTIC' | 'PCT' | 'ANNUITY'` but it is never imported or referenced anywhere else. The `rate_group` fields use `string | null` instead of `RateGroup | null`.
   - **Impact**: None — dead code, no runtime or type-safety effect.
   - **Recommendation**: Either use `RateGroup` in the `rate_group` field types (like `CalcMode` is used for `calc_mode`) or remove the unused export.

2. **Clearing dimension fields in edit mode may not persist to backend**
   - In `handleSubmit()`, dimension fields use `|| undefined` coercion (e.g., `rate_group: form.rate_group || undefined`). When a user clears a previously-set select field, Element Plus sets the value to `''` (empty string). The `'' || undefined` expression evaluates to `undefined`, meaning the field is omitted from the payload. The backend's `FeeRateUpdateIn` will then not receive the field and will not update it to `null`.
   - **Impact**: Low — a user cannot "clear" a dimension field back to null via the edit form. They can only change it to another value. This matches the pattern used by other fields (description, currency) in the same form.
   - **Recommendation**: For a future enhancement, consider using explicit `null` coercion for clearable selects (e.g., `rate_group: form.rate_group || null`).

3. **`calc_mode` unsafe cast**
   - `fees.ts:62` uses `(input.calc_mode as CalcMode) ?? null`. If the backend ever returns a `calc_mode` value outside the `CalcMode` union type, TypeScript won't catch it at runtime.
   - **Impact**: Negligible — the backend constrains values via the `CalcMode` enum, so invalid values cannot occur in practice.

---

## Recommendations

1. **For future batches**: Consider establishing a shared `labelMap` utility that centralizes Chinese label translations for enum values across modules (fees, cases, documents all have overlapping enums like CaseType, PatentCategory).

2. **RateGroup alignment**: Either apply `RateGroup` type to the `rate_group` fields consistently (like `CalcMode` is applied to `calc_mode`) or remove the unused export to keep the codebase clean.

3. **Clearable field null persistence**: If users need the ability to "unset" a previously-set dimension field, update the payload coercion to send explicit `null` values for cleared selects.

---

## Summary

The FC3 implementation is thorough, well-structured, and follows the architect plan precisely. All 9 B4 dimension fields flow correctly from backend response → mapper → frontend type → table display → form input → create/update payload → backend request. The Chinese localization is complete. Quality gates pass. No blocking issues found.
