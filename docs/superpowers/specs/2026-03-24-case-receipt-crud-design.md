# FR-FE-07: Case Receipt CRUD — Design Spec

**Date**: 2026-03-24
**Priority**: P0 #2 (from FPMS_SPEC2_2nd_Review.md)
**SPEC Reference**: SPEC 2.0 §5.11 FR-FE-07, §5.11.3 Fee Status Query
**Status**: Approved

---

## 1. Overview

Implement manual case receipt registration (个案收款登记) as a supplement to the existing auto-allocation flow. The existing `_allocate_offset_to_receipts` / `_reverse_offset_from_receipts` remain the primary mechanism. Manual CRUD enables edge cases: historical import, non-bill receipts, and metadata editing.

### Decisions

| Decision | Choice |
|----------|--------|
| Manual registration mode | Supplement-only (auto-allocation remains primary) |
| Schema change | Phase 0-EXT exception — add 4 columns via migration |
| Permissions | `CaseReceipt.Read`, `.Create`, `.Update` — no delete |
| List endpoint filters | Full SPEC: client_id, fee_type, is_arrears, is_commissionable, currency, date range, case_no |
| Frontend scope | Cross-case list page + inline dialog on case detail |
| Auto-calc flags | Server-side default + user override |

---

## 2. Data Model Changes

### New Migration: `pe_fr_fe_07_case_receipt_ext`

**Revision ID**: Auto-assigned by Alembic. File will be named `pe_fr_fe_07_case_receipt_ext.py` with the revision slug `pe_fr_fe_07_01`. Depends on the latest existing revision (chain head at implementation time).

Adds 4 columns to `t_case_receipt` using `batch_alter_table` (SQLite compat). Forward-only. Idempotent column existence check.

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `fee_name` | String(128) | Yes | NULL | Display name for fee code |
| `due_date` | Date | Yes | NULL | Bill/contract due date for aging |
| `is_prepayment` | Boolean | Yes | `0` | ReceivedAmt > ReceivableAmt |
| `remark` | String(512) | Yes | NULL | Free-text notes |

### Model Update (`billing/models.py`)

Add the 4 new `mapped_column` fields to existing `CaseReceipt` class:

```python
fee_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
is_prepayment: Mapped[bool | None] = mapped_column(
    Boolean, nullable=True, server_default=text("0")
)
remark: Mapped[str | None] = mapped_column(String(512), nullable=True)
```

---

## 3. API Contract

### New Schemas (`billing/schemas.py`)

**CaseReceiptCreate**:

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `case_id` | str | Yes | FK exists check |
| `fee_type` | str \| None | No | GOV / SERVICE / MISC |
| `fee_code` | str \| None | No | |
| `fee_name` | str \| None | No | |
| `year_no` | int \| None | No | |
| `currency` | str | No (default CNY) | |
| `receivable_amt` | Decimal | Yes | >= 0 (V-CR-01) |
| `received_amt` | Decimal | Yes | >= 0 (V-CR-01) |
| `last_receipt_date` | date \| None | No | |
| `due_date` | date \| None | No | |
| `is_arrears` | bool \| None | No | Server default if None |
| `is_prepayment` | bool \| None | No | Server default if None |
| `is_commissionable` | bool \| None | No | |
| `invoice_no` | str \| None | No | |
| `remark` | str \| None | No | |

**CaseReceiptUpdate** (partial — all fields optional):

Same fields as Create except `case_id` is excluded (immutable after creation).

**CaseReceiptResponse** (updated — complete field list):

| Field | Type |
|-------|------|
| `id` | str |
| `case_id` | str |
| `fee_type` | str \| None |
| `currency` | str |
| `receivable_amt` | Decimal |
| `received_amt` | Decimal |
| `last_receipt_date` | date \| None |
| `fee_code` | str \| None |
| `fee_name` | str \| None | *(NEW)* |
| `year_no` | int \| None |
| `due_date` | date \| None | *(NEW)* |
| `is_arrears` | bool \| None |
| `is_prepayment` | bool \| None | *(NEW)* |
| `is_commissionable` | bool \| None |
| `invoice_no` | str \| None |
| `remark` | str \| None | *(NEW)* |
| `bills` | list[CaseReceiptBillResponse] |

**CaseReceiptListItem**: Same fields as CaseReceiptResponse (without `bills`) plus `case_no: str | None` and `client_name: str | None` (joined from t_case/t_client).

**CaseReceiptListResponse** (matches existing pagination envelope):
```python
{ "items": list[CaseReceiptListItem], "page": int, "page_size": int, "total": int }
```

### New Endpoints

| Method | Path | Permission | Response | Description |
|--------|------|-----------|----------|-------------|
| `POST` | `/api/v1/case-receipts` | `CaseReceipt.Create` | 201 + CaseReceiptResponse | Manual receipt registration |
| `PUT` | `/api/v1/case-receipts/{id}` | `CaseReceipt.Update` | 200 + CaseReceiptResponse | Edit receipt fields |
| `GET` | `/api/v1/case-receipts` | `CaseReceipt.Read` | 200 + CaseReceiptListResponse | Cross-case list with filters |

**Existing endpoint unchanged**: `GET /api/v1/cases/{case_id}/receipts`

### List Filters (query params)

| Param | Type | Description |
|-------|------|-------------|
| `client_id` | str | Filter by client (joins case → client) |
| `case_no` | str | Keyword search (LIKE) on case_no |
| `fee_type` | str | GOV / SERVICE / MISC |
| `is_arrears` | bool | Arrears filter |
| `is_commissionable` | bool | Commission eligibility filter |
| `currency` | str | Currency filter |
| `date_from` | date | last_receipt_date >= |
| `date_to` | date | last_receipt_date <= |
| `page` | int | Default 1 |
| `page_size` | int | Default 20, max 100 |

### Validation Rules

- **V-CR-01**: `receivable_amt >= 0`, `received_amt >= 0` — Pydantic `Field(ge=0)`
- **V-CR-02**: If `received_amt > receivable_amt` and `is_prepayment is None` in payload → server sets `is_prepayment = True`
- **V-CR-03**: If `received_amt < receivable_amt` and `is_arrears is None` in payload → server sets `is_arrears = True`
- **Case exists**: Validate `case_id` FK on create → 404 if not found

### Permission Seeding

`CaseReceipt.Read` already exists in `ROLE_PERMISSIONS["Admin"]` (rbac/service.py line 29). Must add `CaseReceipt.Create` and `CaseReceipt.Update` to the Admin role's permission list in `rbac/service.py`. This is a code edit, not a migration — permissions are seeded via `seed_dev.py`.

---

## 4. Service Layer

### `create_case_receipt(db: Session, payload: CaseReceiptCreate) → CaseReceipt`

1. Validate case_id exists (404 if not)
2. Apply V-CR-02/V-CR-03 defaults: check `payload.is_arrears is None` / `payload.is_prepayment is None` (Pydantic `Field(default=None)` — omitted fields arrive as `None`; explicit `null` in JSON also arrives as `None`; both trigger server default). If user passes `true`/`false` explicitly, server respects it.
3. UUID auto-generated by `UUIDPrimaryKeyMixin` default
4. `created_by` / `updated_by` left as NULL (matches existing billing service pattern — AuditMixin fields are nullable, not auto-populated)
5. Return created record

### `update_case_receipt(db: Session, receipt_id: str, payload: CaseReceiptUpdate) → CaseReceipt`

1. Find receipt by id (404 if not)
2. Apply partial update: iterate `payload.model_dump(exclude_unset=True)` — only fields explicitly provided in the request body are updated. Fields omitted from JSON are not touched.
3. Recompute V-CR-02/V-CR-03 defaults: only if `receivable_amt` or `received_amt` was in the update AND the corresponding flag was NOT in the update
4. `updated_by` left as NULL (matches existing pattern)
5. Return updated record

### `list_case_receipts(db: Session, filters: dict) → dict`

1. Join `t_case_receipt` → `t_case` → `t_client` for `case_no` / `client_name` (eager join, no N+1)
2. Apply all filter params (client_id via case.client_id, case_no LIKE, fee_type ==, etc.)
3. Count total before pagination
4. Apply `page` / `page_size` offset/limit
5. Order by `CASE WHEN last_receipt_date IS NULL THEN 1 ELSE 0 END, last_receipt_date DESC, created_at DESC` (SQLite-compatible NULLS LAST)
6. Return `{"items": [...], "page": N, "page_size": N, "total": N}`

**No changes** to existing `_allocate_offset_to_receipts` / `_reverse_offset_from_receipts`.

---

## 5. Frontend

### 5a. Cross-case List Page (`CaseReceiptList.vue`)

- **Route**: `/billing/case-receipts`
- **Menu label**: `个案收款登记`
- **Layout**: Standard list page pattern (matches `BillList.vue`)
- **Filter bar**: 客户、案卷号、费用类型、是否欠款、是否可提成、币种、收款日期范围
- **Table columns**: 案卷号、客户名称、费用代码、费用名称、年度、费用类型、应收金额、实收金额、币种、是否欠款、是否预收、收款日期、到期日、发票号
- **Row actions**: 编辑 → opens `CaseReceiptDialog.vue`
- **Toolbar**: `新增收款记录` button → opens `CaseReceiptDialog.vue` in create mode
- **Pagination**: el-pagination, 20 per page

### 5b. Create/Edit Dialog (`CaseReceiptDialog.vue`)

Shared `el-dialog` for create and edit.

- **Title**: `新增收款记录` / `编辑收款记录`
- **Form fields** (all 简体中文 labels):

| Label | Component | Binding | Notes |
|-------|-----------|---------|-------|
| 案卷 | el-select (remote) | `case_id` | Create only; disabled on edit |
| 费用类型 | el-select | `fee_type` | GOV/SERVICE/MISC |
| 费用代码 | el-input | `fee_code` | |
| 费用名称 | el-input | `fee_name` | |
| 年度 | el-input-number | `year_no` | |
| 币种 | el-select | `currency` | Default CNY |
| 应收金额 | el-input-number | `receivable_amt` | min=0, precision=2 |
| 实收金额 | el-input-number | `received_amt` | min=0, precision=2 |
| 收款日期 | el-date-picker | `last_receipt_date` | |
| 到期日 | el-date-picker | `due_date` | |
| 是否欠款 | el-checkbox | `is_arrears` | Auto-hint text |
| 是否预收 | el-checkbox | `is_prepayment` | Auto-hint text |
| 是否可提成 | el-checkbox | `is_commissionable` | |
| 发票号 | el-input | `invoice_no` | |
| 备注 | el-input (textarea) | `remark` | |

- **Actions**: 确认 / 取消
- **Client-side hint**: When `received_amt < receivable_amt`, show "实收金额小于应收金额，将标记为欠款"

### 5e. Frontend Error Messages & Hints (简体中文)

| Scenario | Message |
|----------|---------|
| Case not found (create) | `案卷不存在` |
| Amount negative (client-side) | `金额不能为负数` |
| Save success | `保存成功` |
| Save failure | `保存失败，请重试` |
| Load failure | `加载数据失败` |
| Arrears auto-hint | `实收金额小于应收金额，将标记为欠款` |
| Prepayment auto-hint | `实收金额大于应收金额，将标记为预收` |
| Required field missing | `请填写必填项` |
| No data in list | `暂无数据` |

### 5c. Case Detail Integration

- On `CaseReceiptsSummary.vue`, add `新增收款记录` button
- Opens `CaseReceiptDialog.vue` with `case_id` pre-filled and locked

### 5d. API Client (`billing.ts`)

```typescript
createCaseReceipt(payload): Promise<CaseReceiptResponse>
updateCaseReceipt(id, payload): Promise<CaseReceiptResponse>
listCaseReceipts(filters): Promise<CaseReceiptListResponse>
```

---

## 6. Testing & Acceptance Criteria

### Backend Tests (`tests/test_case_receipt_crud.py`)

| Test | Description |
|------|-------------|
| `test_create_case_receipt_success` | POST valid → 201, fields match |
| `test_create_case_receipt_invalid_case` | POST non-existent case → 404 |
| `test_create_case_receipt_negative_amt` | POST amt < 0 → 422 |
| `test_create_auto_arrears` | received < receivable, no flag → is_arrears=True |
| `test_create_auto_prepayment` | received > receivable, no flag → is_prepayment=True |
| `test_create_user_override_arrears` | received < receivable, is_arrears=False → respected |
| `test_create_user_override_prepayment` | received > receivable, is_prepayment=False → respected |
| `test_update_case_receipt_success` | PUT partial → 200, changed only |
| `test_update_recompute_flags` | PUT new amounts, no flag → flags recomputed |
| `test_update_not_found` | PUT non-existent → 404 |
| `test_list_case_receipts_no_filter` | GET list → 200, paginated |
| `test_list_filter_by_client` | GET client_id → matching only |
| `test_list_filter_by_arrears` | GET is_arrears=true → arrears only |
| `test_list_filter_by_date_range` | GET date range → correct range |
| `test_list_pagination` | GET page=2 → correct offset |
| `test_permissions_create` | POST no perm → 403 |
| `test_permissions_update` | PUT no perm → 403 |
| `test_manual_receipt_no_conflict_with_auto` | Manual create does not interfere with offset auto-allocation |

### Migration Test

`rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py` → success

### Frontend Quality Gates

- `npm run lint` → PASS
- `npm run typecheck` → PASS
- `npm run build` → PASS

### Acceptance Checklist

- [ ] Migration adds 4 columns, clean rebuild passes
- [ ] POST /case-receipts creates record with correct defaults
- [ ] PUT /case-receipts/{id} partial updates work
- [ ] GET /case-receipts list with all filters works
- [ ] V-CR-01/02/03 validation rules enforced
- [ ] Permissions enforced (Create/Update/Read)
- [ ] Existing auto-allocation flow unaffected
- [ ] Frontend list page renders with filters (all 简体中文)
- [ ] Frontend dialog creates/edits records
- [ ] Case detail page "新增收款记录" button works
- [ ] All 18 backend tests pass
- [ ] Frontend lint + typecheck + build pass

---

## Appendix: File Impact Summary

| File | Change |
|------|--------|
| `backend/alembic/versions/pe_fr_fe_07_case_receipt_ext.py` | NEW — migration |
| `backend/app/modules/billing/models.py` | EDIT — add 4 columns |
| `backend/app/modules/billing/schemas.py` | EDIT — add Create/Update/ListItem/ListResponse schemas, update Response |
| `backend/app/modules/billing/service.py` | EDIT — add create/update/list functions |
| `backend/app/modules/billing/api.py` | EDIT — add POST/PUT/GET endpoints |
| `backend/app/modules/rbac/service.py` | EDIT — add CaseReceipt.Create, CaseReceipt.Update to ROLE_PERMISSIONS |
| `backend/tests/test_case_receipt_crud.py` | NEW — 18 tests |
| `frontend/src/api/billing.ts` | EDIT — add 3 API functions |
| `frontend/src/api/billing.types.ts` | EDIT — add CaseReceiptCreate/Update/ListResponse types |
| `frontend/src/modules/billing/pages/CaseReceiptList.vue` | NEW — list page |
| `frontend/src/modules/billing/components/CaseReceiptDialog.vue` | NEW — create/edit dialog |
| `frontend/src/modules/cases/components/CaseReceiptsSummary.vue` | EDIT — add create button |
| `frontend/src/router/index.ts` | EDIT — add route |

---

**Document Version**: 1.1 (post spec-review fixes)
**Author**: Claude Code (brainstorming session)
**Approved by**: User (2026-03-24)
**Spec Review**: Iteration 1 — 4 CRITICAL + 5 WARN resolved
