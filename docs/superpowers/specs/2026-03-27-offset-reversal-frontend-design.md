# P0 #4 — 冲销反转前端 (Offset Reversal UI)

**Date**: 2026-03-27
**Story**: US-BL-05 / FR-BL-06 — 冲销反转
**Priority**: P0
**Phase**: 3 (no schema changes — read-only endpoint + frontend)

---

## 1. Goal

Expose offset reversal to users via two entry points:

1. **Independent OffsetList page** (`/billing/offsets`) — full offset management with filters, pagination, and reversal action.
2. **BillDetail embedded tab** — already implemented in `BillDetail.vue` (lines 224-277), blocked only by the missing backend list endpoint.

The backend `POST /api/v1/offsets/{id}/reverse` service is complete and tested. The frontend API client `reverseOffset()` is complete. The gap is:

- **Backend**: No `GET /api/v1/offsets` list endpoint exists.
- **Frontend**: `getOffsets()` in `billing.ts` is a stub returning `{ items: [], total: 0 }`.
- **Frontend**: No `OffsetList.vue` page, no route, no menu entry.

## 2. Current State Audit

| Component | File | Status |
|-----------|------|--------|
| Offset model | `backend/app/modules/billing/models.py` — `Offset` | Done |
| `reverse_offset()` service | `backend/app/modules/billing/service.py:701-752` | Done + tested |
| `POST /offsets/{id}/reverse` | `backend/app/modules/billing/api.py:485-523` | Done |
| `POST /offsets` (create) | `backend/app/modules/billing/api.py:439-482` | Done |
| `GET /offsets` (list) | — | **MISSING** |
| `OffsetResponse` schema | `backend/app/modules/billing/schemas.py:132-140` | Done (minimal) |
| `OffsetListItemResponse` schema | — | **MISSING** (need `bill_no`, `reversed_at`, `created_at`) |
| Frontend `reverseOffset()` | `frontend/src/api/billing.ts:353-356` | Done |
| Frontend `getOffsets()` | `frontend/src/api/billing.ts:328-340` | **STUB** — returns empty |
| Frontend `OffsetListItem` type | `frontend/src/api/billing.types.ts:145-155` | Done |
| BillDetail offsets tab | `frontend/src/modules/billing/pages/BillDetail.vue:224-277` | Done (blocked by stub) |
| `OffsetList.vue` page | — | **MISSING** |
| Route `/billing/offsets` | — | **MISSING** |
| Menu entry 冲销管理 | — | **MISSING** |

## 3. Backend API Contract

### 3.1 `GET /api/v1/offsets` — List offsets

**Permission**: `Billing.Read` via `_perm: None = Depends(require_perm("Billing.Read"))`

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | int | no | 1 | Page number (>= 1) |
| `page_size` | int | no | 20 | Items per page (1-100) |
| `bill_id` | str | no | — | Filter by bill UUID |
| `is_reversed` | bool | no | — | Filter by reversal status |

**Response** (200):

```json
{
  "items": [
    {
      "id": "uuid-string",
      "payment_line_id": "uuid-string",
      "bill_id": "uuid-string",
      "bill_no": "BILL-001",
      "offset_amt": "5000.00",
      "offset_date": "2026-03-20",
      "is_reversed": false,
      "reversed_at": null,
      "created_at": "2026-03-20T10:00:00"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 42
}
```

**Implementation Notes**:
- Join `Offset` → `Bill` to resolve `bill_no`.
- Use `created_at` from `AuditMixin` (already on Offset via mixin).
- Use `reversed_at` from Offset model (already exists).
- Pagination: `query.count()` for total, `.offset((page-1)*page_size).limit(page_size)`.
- SQLite compatible — no PG-only functions.

### 3.2 New Schema: `OffsetListItemResponse`

```python
class OffsetListItemResponse(BaseModel):
    id: str
    payment_line_id: str
    bill_id: str
    bill_no: str | None = None
    offset_amt: Decimal
    offset_date: date | None = None
    is_reversed: bool
    reversed_at: str | None = None   # ISO datetime string
    created_at: str | None = None    # ISO datetime string
```

### 3.3 Existing Endpoints (unchanged)

- `POST /api/v1/offsets` — create offset (Permission: `Payment.Create`)
- `POST /api/v1/offsets/{offset_id}/reverse` — reverse offset (Permission: `Billing.Edit`)

## 4. Frontend Design

### 4.1 API Client Update: `getOffsets()` in `billing.ts`

Replace the stub implementation (lines 328-340) with a real API call:

```typescript
export async function getOffsets(
    params: { page?: number; page_size?: number; bill_id?: string; is_reversed?: boolean } = {}
): Promise<Pagination<OffsetListItem>> {
    const response = await http.get<{
        items: BackendOffset[]
        page: number
        page_size: number
        total: number
    }>('/offsets', { params })
    return {
        items: response.data.items.map(mapOffset),
        page: response.data.page,
        page_size: response.data.page_size,
        total: response.data.total,
    }
}
```

### 4.2 OffsetListItem Type Update (`billing.types.ts`)

Add `bill_no` field (currently missing from the type but will be returned by the new endpoint):

```typescript
export interface OffsetListItem {
    id: string
    payment_line_id: string
    bill_id: string
    bill_no?: string          // NEW — from enriched backend response
    amount: number
    currency: string
    offset_date?: string
    is_reversed: boolean
    reversed_at?: string
    created_at: string
}
```

### 4.3 `OffsetList.vue` — New Page

**Path**: `frontend/src/modules/billing/pages/OffsetList.vue`
**Route**: `/billing/offsets`, name: `offsets`

**Layout**:
- Page header: "冲销管理"
- Filter bar:
  - 反转状态: `<el-select>` with options: 全部 / 正常 / 已反转
  - 查询 / 重置 buttons
- Table columns:
  - 冲销金额 (right-aligned, mono-num)
  - 冲销日期
  - 账单号 (link to BillDetail)
  - 状态 (`<el-tag>`: 正常=success, 已反转=danger)
  - 反转时间
  - 操作 (反转 button via `ElMessageBox.confirm`, hidden if already reversed)
- Pagination: server-side, `<el-pagination>` bound to page/page_size/total

**Reversal Confirm Dialog** (via `ElMessageBox.confirm`):
```
确认反转冲销

冲销金额：¥5,000.00
关联账单：BILL-001

反转后，账单余额将恢复，付款行可用金额将增加。此操作不可撤销。

[取消]  [确认反转]
```

**UI Language**: All text in simplified Chinese.

### 4.4 BillDetail.vue Offsets Tab

**No code changes needed.** The existing tab (lines 224-277) already:
- Calls `getOffsets({ bill_id })` to fetch offsets
- Renders offset table with date, amount, status, action columns
- Has `handleReverseOffset()` calling `reverseOffset()` API
- Shows `el-popconfirm` before reversal
- Refreshes bill + offsets after reversal

Once the backend endpoint exists and `getOffsets()` makes a real API call, this tab will work automatically.

### 4.5 Route Addition (`router/index.ts`)

```typescript
{ path: 'billing/offsets', name: 'offsets', component: () => import('../modules/billing/pages/OffsetList.vue') },
```

### 4.6 Menu Addition (`menu.ts`)

Add under `finance` group, after `payments`:

```typescript
{ key: 'offsets', label: '冲销管理', icon: '🔄', route: '/billing/offsets', requiredPerms: [Perms.BILLING_READ] },
```

## 5. Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| AC-1 | `GET /api/v1/offsets` returns paginated offset list | `pytest` — new test |
| AC-2 | `GET /api/v1/offsets?bill_id=X` filters by bill | `pytest` — new test |
| AC-3 | `GET /api/v1/offsets?is_reversed=true` filters by status | `pytest` — new test |
| AC-4 | Response includes `bill_no` enrichment from joined Bill | `pytest` — new test |
| AC-5 | OffsetList.vue renders offset table with all columns | Manual + build passes |
| AC-6 | OffsetList.vue filter bar works (is_reversed) | Manual verification |
| AC-7 | OffsetList.vue pagination works | Manual verification |
| AC-8 | OffsetList.vue reversal button only on non-reversed rows | Manual + build passes |
| AC-9 | OffsetList.vue `ElMessageBox.confirm` → API → refresh | Manual verification |
| AC-10 | BillDetail offsets tab shows real data | Manual verification |
| AC-11 | BillDetail reversal button works end-to-end | Manual verification |
| AC-12 | Menu shows 冲销管理 under 财务 group | Manual verification |
| AC-13 | `pytest --tb=short` — all tests pass | CI gate |
| AC-14 | `npm run lint && npm run typecheck && npm run build` — passes | CI gate |

## 6. File Impact Summary

| # | File | Action | Atomic Task |
|---|------|--------|-------------|
| 1 | `backend/app/modules/billing/schemas.py` | ADD `OffsetListItemResponse` | BE-1 |
| 2 | `backend/app/modules/billing/service.py` | ADD `list_offsets()` function | BE-2 |
| 3 | `backend/app/modules/billing/api.py` | ADD `GET /offsets` endpoint | BE-3 |
| 4 | `backend/tests/test_offset_list.py` | NEW — tests for list endpoint | BE-TEST |
| 5 | `frontend/src/api/billing.types.ts` | UPDATE — add `bill_no` to `OffsetListItem` | FE-1 |
| 6 | `frontend/src/api/billing.ts` | UPDATE — replace `getOffsets` stub | FE-2 |
| 7 | `frontend/src/modules/billing/pages/OffsetList.vue` | NEW — offset list page | FE-3 |
| 8 | `frontend/src/router/index.ts` | UPDATE — add `/billing/offsets` route | FE-4 |
| 9 | `frontend/src/constants/menu.ts` | UPDATE — add 冲销管理 menu item | FE-5 |

## 7. Non-Closure Boundaries

- **No schema migration**: No new DB columns or tables. Phase 3 compatible.
- **No changes to `reverse_offset()` service**: Backend reversal logic is complete.
- **No changes to `BillDetail.vue`**: Existing offsets tab works once API is connected.
- **No changes to `OffsetCreateSchema` or `POST /offsets`**: Create flow unchanged.

## 8. Risks

| Risk | Mitigation |
|------|-----------|
| `getOffsets()` stub callers may not expect real data shape | Existing `BillDetail.vue` already handles the shape correctly |
| `OffsetListItem.bill_no` field is new | Frontend type already allows optional fields; `mapOffset` handles missing fields |
| SQLite `CURRENT_TIMESTAMP` in `created_at` format | `AuditMixin` already handles this consistently across all models |
