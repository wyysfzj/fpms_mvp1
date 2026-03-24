# B4 Reviewer Report

> Reviewer: review-agent
> Date: 2026-02-26
> Batch: B4 — FeeRate Dimensions + CalcMode Stub

---

## Summary

All B4 deliverables have been implemented correctly, matching the approved architect plan. The migration adds 9 new nullable columns to `t_fee_rate` with SQLite-compatible `batch_alter_table`. The `CalcMode` enum, model fields, schemas, service filters, API query params, and `calculate_fee_amount()` stub are all in place. All 11 B4-specific tests pass, and the full suite of 123 tests passes with zero failures. No blockers found.

---

## Files Reviewed

| # | File | Status | Lines |
|---|------|--------|-------|
| 1 | `alembic/versions/b4_fee_rate_dimensions.py` | NEW | 52 |
| 2 | `app/modules/fees/enums.py` | MODIFIED | 22 |
| 3 | `app/modules/fees/models.py` | MODIFIED | 90 |
| 4 | `app/modules/fees/schemas.py` | MODIFIED | 142 |
| 5 | `app/modules/fees/service.py` | MODIFIED | 371 |
| 6 | `app/modules/fees/api.py` | MODIFIED | 540 |
| 7 | `tests/test_b4_fee_rate_dims.py` | NEW | 285 |

Reference documents also reviewed:
- `artifacts/B4_plan/01_Architect_Plan.md`
- `artifacts/B4_plan/findings.md`

---

## Checklist Results

### 1. Migration (`alembic/versions/b4_fee_rate_dimensions.py`)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1.1 | Uses `batch_alter_table` for SQLite compat | PASS | Line 42: `with op.batch_alter_table("t_fee_rate") as batch_op:` |
| 1.2 | Idempotent column-exists check | PASS | Line 28: `existing = {col["name"] for col in insp.get_columns(...)}` + Line 44: `if col_name not in existing` |
| 1.3 | All 9 columns nullable | PASS | Line 46: `nullable=True` for every column |
| 1.4 | `calc_mode` server_default=`text("'FIXED'")` | PASS | Line 35 |
| 1.5 | `allow_reduction` server_default=`text("0")` | PASS | Line 37 |
| 1.6 | `effective_from` and `effective_to` are Date type | PASS | Lines 38-39: `sa.Date()` |
| 1.7 | Correct revision chain | PASS | Line 16: `down_revision = "b2_doc_reply_01"` |
| 1.8 | Table existence guard | PASS | Line 25: `if not insp.has_table("t_fee_rate"): return` |

### 2. Model (`app/modules/fees/models.py`)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 2.1 | All 9 fields added with correct types | PASS | Lines 77-89: rate_group(String32), country_code(String10), case_type(String32), patent_category(String32), calc_mode(String16), calc_params(Text), allow_reduction(Boolean), effective_from(Date), effective_to(Date) |
| 2.2 | Correct imports | PASS | Line 3: `from datetime import date`, Line 6: `Date` from sqlalchemy |
| 2.3 | No changes to FeeDraft/FeeItem | PASS | Lines 13-63 unchanged |
| 2.4 | server_defaults match migration | PASS | calc_mode: `text("'FIXED'")` (L82), allow_reduction: `text("0")` (L86) |

### 3. Schema (`app/modules/fees/schemas.py`)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 3.1 | FeeRateCreateIn: 9 optional fields | PASS | Lines 91-99, all typed `X | None = None` |
| 3.2 | FeeRateUpdateIn: 9 optional fields | PASS | Lines 108-116, all typed `X | None = None` |
| 3.3 | FeeRateOut: calc_mode as `str | None` (not enum) | PASS | Line 133: `calc_mode: str | None = None` |
| 3.4 | CalcMode import added | PASS | Line 9: `from app.modules.fees.enums import CalcMode, FeeDraftStatus, FeeType` |
| 3.5 | date_type import for effective_from/to | PASS | Line 3: `from datetime import date as date_type` |
| 3.6 | CreateIn uses `CalcMode | None` (typed enum) | PASS | Line 95 |
| 3.7 | UpdateIn uses `CalcMode | None` (typed enum) | PASS | Line 110 |

### 4. Service (`app/modules/fees/service.py`)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 4.1 | `list_fee_rates`: 5 new filter params | PASS | Lines 280-295: rate_group, country_code, case_type, patent_category, calc_mode |
| 4.2 | `create_fee_rate`: 9 new fields in constructor | PASS | Lines 315-323: all 9 fields passed explicitly |
| 4.3 | `create_fee_rate`: calc_mode stored as `.value` | PASS | Line 319: `data.calc_mode.value if data.calc_mode else None` |
| 4.4 | `calculate_fee_amount`: FIXED returns default_amount | PASS | Lines 360-361 |
| 4.5 | `calculate_fee_amount`: other modes log warning | PASS | Lines 363-370: `logger.warning(...)` with rate details |
| 4.6 | `calculate_fee_amount`: None default_amount -> Decimal("0") | PASS | Line 357: `rate.default_amount if rate.default_amount is not None else Decimal("0")` |
| 4.7 | `calculate_fee_amount`: None calc_mode falls back to FIXED | PASS | Line 358: `getattr(rate, "calc_mode", None) or "FIXED"` |
| 4.8 | Logger properly configured | PASS | Line 25: `logger = logging.getLogger(__name__)` |
| 4.9 | `update_fee_rate` unchanged (generic setattr loop) | PASS | Lines 331-348: no changes needed, works with new fields automatically |

### 5. API (`app/modules/fees/api.py`)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 5.1 | 5 new Query params on `get_fee_rates` | PASS | Lines 420-424: rate_group, country_code, case_type, patent_category, calc_mode |
| 5.2 | All 5 new params wired into filters dict | PASS | Lines 451-455 |
| 5.3 | Existing endpoints unchanged | PASS | No modifications to draft/item endpoints |

### 6. Tests (`tests/test_b4_fee_rate_dims.py`)

| # | Test | Category | Status |
|---|------|----------|--------|
| T1 | `test_create_fee_rate_with_dimensions` | CRUD - Create | PASS |
| T2 | `test_create_fee_rate_without_dimensions` | Backward compat | PASS |
| T3 | `test_update_fee_rate_dimensions` | CRUD - Update | PASS |
| T4 | `test_list_fee_rates_filter_by_rate_group` | Filter | PASS |
| T5 | `test_list_fee_rates_filter_by_country_code` | Filter | PASS |
| T6 | `test_list_fee_rates_filter_by_calc_mode` | Filter | PASS |
| T7 | `test_calc_fee_amount_fixed_mode` | Unit - calc stub | PASS |
| T8 | `test_calc_fee_amount_fixed_is_default` | Unit - calc stub | PASS |
| T9 | `test_calc_fee_amount_per_claim_stub` | Unit - calc stub | PASS |
| T10 | `test_calc_fee_amount_none_default_amount` | Unit - calc stub | PASS |
| T11 | `test_fee_rate_out_schema_has_new_fields` | Schema validation | PASS |

**Coverage**: CRUD (3), Filtering (3), Calculation stub (4), Schema (1) = 11 tests total.

### 7. Constraints

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 7.1 | All new columns nullable | PASS | Migration and model both use `nullable=True` |
| 7.2 | calc_params not parsed | PASS | Stored as `Text`, no JSON validation |
| 7.3 | No PER_CLAIM/PER_PAGE/TIER logic | PASS | Stub returns default_amount with warning log |
| 7.4 | No UI changes | PASS | No frontend files modified |
| 7.5 | SQLite compatible | PASS | `batch_alter_table`, `text()` defaults, no PG-only features |
| 7.6 | Backward compatible | PASS | T2 confirms creation without new fields works |

---

## Issues Found

### BLOCKER
_None_

### WARNING
_None_

### SUGGESTION

1. **calc_mode/allow_reduction nullable semantics (LOW)** — In `create_fee_rate`, explicit `None` is passed for `calc_mode` and `allow_reduction` when not provided by the client, which overrides the DB `server_default` (`'FIXED'` and `0` respectively). This means records created via the API without these fields will have `NULL` instead of the server default. Test T2 correctly accounts for this with `assert data["calc_mode"] in (None, "FIXED")`. This is acceptable for MVP — a future enhancement could omit these fields from the constructor when not provided, letting the DB default apply.

2. **Enum serialization consistency (LOW)** — `create_fee_rate` extracts `data.calc_mode.value` explicitly (Line 319), while `update_fee_rate` passes the enum instance directly via the generic `setattr` loop. Both work correctly because `CalcMode(str, Enum)` is a `str` subclass, but the approaches differ. Not a bug — just a code style observation.

3. **No filter tests for case_type and patent_category (LOW)** — Tests cover filter by `rate_group`, `country_code`, and `calc_mode` (T4-T6) but not `case_type` or `patent_category`. The filter implementation is identical pattern for all 5, so risk is minimal. Could add coverage in a future batch.

---

## Quality Gate Results

| Check | Command | Result |
|-------|---------|--------|
| Lint | `ruff check app/modules/fees/ tests/test_b4_fee_rate_dims.py alembic/versions/b4_fee_rate_dimensions.py` | **All checks passed** |
| B4 Tests | `pytest tests/test_b4_fee_rate_dims.py -v` | **11 passed** in 2.18s |
| Full Suite | `pytest --tb=short -q` | **123 passed** in 26.20s |

---

## Verdict

### **APPROVED**

All acceptance criteria met. Implementation matches the approved architect plan precisely. No blockers or warnings. Three low-priority suggestions noted for future consideration. Quality gate passes clean: lint clean, 11/11 B4 tests pass, 123/123 full suite passes.
