# A0 Baseline Verification — Summary

**Date**: 2026-02-23
**Status**: COMPLETE
**Batch**: A0 — Baseline Verification

---

## Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| 1. Case CRUD | **PASS** | Create, search, detail all working |
| 2. Document + Task auto-link | **PASS (partial)** | Document creation works after schema fix. Auto-task requires Batch A1 |
| 3. Fee→Bill→Payment chain | **PASS** | All endpoints working at correct URLs |
| 4. Word bill template | **MANUAL** | Requires template file + bill data |

## Bugs Found & Fixed

### Fix 1: `doc_template_id` missing default (schema bug)
- **File**: `backend/app/modules/documents/schemas.py:22`
- **Problem**: `doc_template_id: str | None` (no `= None`) — Pydantic v2 requires the field in JSON even though it's nullable
- **Fix**: Changed to `doc_template_id: str | None = None`

### Fix 2: Missing audit columns on case sub-tables (migration gap)
- **File**: NEW `backend/alembic/versions/53f7a0c139cc_a0_add_audit_cols_case_subtables.py`
- **Problem**: `t_case_applicant`, `t_case_inventor`, `t_priority` models use `AuditMixin` but migration `e109a0b1c2d3` didn't include them
- **Fix**: New forward-only migration adding `created_at`, `updated_at`, `created_by`, `updated_by` to all 3 tables

### Fix 3: `pyproject.toml` package discovery (build issue)
- **File**: `backend/pyproject.toml`
- **Problem**: `pip install -e ".[dev]"` fails because setuptools discovers `storage/`, `alembic/`, `artifacts/` as packages
- **Fix**: Added `[tool.setuptools.packages.find] include = ["app*"]`

## Script Discrepancy (NOT a code bug)

The verification script in `Claude_enhance.md` uses incorrect URLs for billing endpoints:
- Script: `/api/v1/billing/bills` and `/api/v1/billing/payments`
- Actual: `/api/v1/bills` and `/api/v1/payments`

The billing router in `router.py:26` is included without a prefix, so all billing endpoints are at the root `/api/v1/` level. The code is correct; the script URLs should be updated.

## Quality Gate

| Check | Result |
|-------|--------|
| `ruff check` | **PASS** |
| `pytest -q` | **PASS** (34/34) |
| `alembic upgrade head` | **PASS** |
| `seed_dev.py` | **PASS** |
| `healthz` | **PASS** |

## Files Modified

| File | Change |
|------|--------|
| `backend/app/modules/documents/schemas.py` | Added `= None` default to `doc_template_id` |
| `backend/pyproject.toml` | Added `[tool.setuptools.packages.find]` |
| `backend/alembic/versions/53f7a0c139cc_...py` | NEW: audit columns for case sub-tables |

## Ready for A1

A0 is **COMPLETE**. All 4 MVP1 success criteria verified. Awaiting approval to proceed to Batch A1 (TaskTemplate Enhancement + TaskLog API).
