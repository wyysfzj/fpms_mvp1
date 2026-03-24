# B4 — FeeRate Dimensions + CalcMode Stub — Task Plan

## Status: PLAN COMPLETE — AWAITING APPROVAL

## Batch Scope
Add multi-dimensional fields to T_FeeRate (9 columns) and a CalcMode stub
so the fee rate table can eventually support automated fee calculation.

## Team Composition
| Role | Agent Name | Status |
|------|-----------|--------|
| Architect | architect | Plan Complete |
| Backend Impl | backend-impl | Pending (approval) |
| Test Agent | test-agent | Pending (approval) |
| Reviewer | reviewer | Pending |

## Task Decomposition

### Task 2 — Backend Implementation (backend-impl)

| Sub-task | Description | File |
|----------|------------|------|
| 2A | Alembic migration: add 9 columns to t_fee_rate | `alembic/versions/b4_fee_rate_dimensions.py` (NEW) |
| 2B | Add CalcMode enum (FIXED, PER_CLAIM, PER_PAGE, TIER) | `app/modules/fees/enums.py` |
| 2C | Add 9 mapped_column fields to FeeRate model | `app/modules/fees/models.py` |
| 2D | Extend FeeRateCreateIn, FeeRateUpdateIn, FeeRateOut schemas | `app/modules/fees/schemas.py` |
| 2E | Extend list_fee_rates filters, create_fee_rate fields, add calculate_fee_amount() stub | `app/modules/fees/service.py` |
| 2F | Add 5 new query params to GET /fees/rates endpoint | `app/modules/fees/api.py` |

### Task 3 — Tests (test-agent)

| Sub-task | Description | File |
|----------|------------|------|
| 3A | Write test_b4_fee_rate_dims.py with 11 test cases | `tests/test_b4_fee_rate_dims.py` (NEW) |

Tests cover: CRUD with new fields, backward compat, filtering, calc stub (FIXED, fallback, PER_CLAIM stub, None amount).

### Task 4 — Review (reviewer)

| Sub-task | Description |
|----------|------------|
| 4A | Read all changed files, verify acceptance criteria |
| 4B | Write review_report.md |

## Dependencies
```
2A (Migration) → 2C (Model) → 2D (Schema) → 2E (Service) → 2F (API)
2B (Enum) → 2D (Schema)
2A-2F complete → 3A (Tests can be written in parallel from plan)
3A complete → 4A (Review)
```

## Files Modified (7 total)
| File | Action |
|------|--------|
| `alembic/versions/b4_fee_rate_dimensions.py` | NEW |
| `app/modules/fees/enums.py` | EDIT (+7 lines) |
| `app/modules/fees/models.py` | EDIT (+15 lines) |
| `app/modules/fees/schemas.py` | EDIT (+30 lines) |
| `app/modules/fees/service.py` | EDIT (+40 lines) |
| `app/modules/fees/api.py` | EDIT (+15 lines) |
| `tests/test_b4_fee_rate_dims.py` | NEW (~200 lines) |

## Acceptance Criteria
1. `alembic upgrade head` succeeds on fresh DB
2. `pytest --tb=short` passes (including 11 new B4 tests)
3. `ruff check . && ruff format --check .` passes
4. GET /fees/rates returns new fields in response
5. POST /fees/rates accepts new fields (all optional)
6. PUT /fees/rates/{id} can update new fields
7. GET /fees/rates?rate_group=X filters correctly
8. calculate_fee_amount(rate) returns default_amount for FIXED mode
9. calculate_fee_amount(rate) returns default_amount with warning log for PER_CLAIM/PER_PAGE/TIER
10. Backward compatibility: existing API calls work unchanged
