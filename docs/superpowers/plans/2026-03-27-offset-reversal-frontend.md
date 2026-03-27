# P0 #4 — Offset Reversal UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `GET /api/v1/offsets` list endpoint and `OffsetList.vue` page so users can view, filter, and reverse offsets from both the independent page and BillDetail embedded tab.

**Architecture:** Prereq-heavy single-lane — backend service → schema → endpoint → tests, then frontend types → API client → page → route → menu. Each task is one file, one closure slice. BillDetail.vue requires zero changes (existing tab unblocks automatically).

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Pydantic 2.x (backend); Vue 3, TypeScript, Element Plus (frontend)

**Spec:** `docs/superpowers/specs/2026-03-27-offset-reversal-frontend-design.md`

**Story Shape:**
- `shared_file_density`: low (no shared files across tasks)
- `prereq_dependency_density`: high (BE → FE dependency chain)
- `be_fe_coupling`: medium (API contract connects them)
- `evidence_cost`: low (standard pytest + lint/build)

**Runbook:** `P0-prereq-heavy-story`

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `backend/app/modules/billing/schemas.py` | EDIT | Add `OffsetListItemResponse` schema |
| `backend/app/modules/billing/service.py` | EDIT | Add `list_offsets()` service function |
| `backend/app/modules/billing/api.py` | EDIT | Add `GET /offsets` endpoint |
| `backend/tests/test_offset_list.py` | CREATE | Tests for offset list endpoint |
| `frontend/src/api/billing.types.ts` | EDIT | Add `bill_no` to `OffsetListItem` |
| `frontend/src/api/billing.ts` | EDIT | Update `BackendOffset`, `mapOffset`, replace `getOffsets` stub |
| `frontend/src/modules/billing/pages/OffsetList.vue` | CREATE | Independent offset management page |
| `frontend/src/router/index.ts` | EDIT | Add `/billing/offsets` route |
| `frontend/src/constants/menu.ts` | EDIT | Add 冲销管理 menu item |

---

## Task 1: Backend — Add `OffsetListItemResponse` schema

**Closure slice:** Add one Pydantic response model to `schemas.py`
**Non-closure:** Does NOT add endpoint or service logic
**Files:**
- Modify: `backend/app/modules/billing/schemas.py` (after `OffsetResponse` class, ~line 141)

- [ ] **Step 1: Add `OffsetListItemResponse` to schemas.py**

Add after the existing `OffsetResponse` class (line 141):

```python
class OffsetListItemResponse(BaseModel):
    """Enriched response schema for offset list items."""

    id: str
    payment_line_id: str
    bill_id: str
    bill_no: str | None = None
    offset_amt: Decimal
    offset_date: date | None = None
    is_reversed: bool
    reversed_at: str | None = None
    created_at: str | None = None
```

- [ ] **Step 2: Verify no import changes needed**

`date` and `Decimal` are already imported in `schemas.py`. `BaseModel` and `Field` too. No new imports required.

- [ ] **Step 3: Run lint**

Run: `cd backend && ruff check --fix app/modules/billing/schemas.py && ruff format app/modules/billing/schemas.py`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add backend/app/modules/billing/schemas.py
git commit -m "feat(billing): add OffsetListItemResponse schema (P0-4 BE-1)"
```

---

## Task 2: Backend — Add `list_offsets()` service function

**Closure slice:** Add one service function to `service.py`
**Non-closure:** Does NOT wire endpoint in `api.py`
**Files:**
- Modify: `backend/app/modules/billing/service.py` (add function after existing offset functions)

- [ ] **Step 1: Identify insertion point**

The `reverse_offset()` function ends around line 752. Add `list_offsets()` after it.

- [ ] **Step 2: Add `list_offsets()` function**

```python
def list_offsets(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    bill_id: str | None = None,
    is_reversed: bool | None = None,
) -> tuple[list[Offset], int]:
    """Return paginated offset list with optional filters.

    Returns (items, total) tuple.
    """
    query = db.query(Offset)

    if bill_id is not None:
        query = query.filter(Offset.bill_id == bill_id)
    if is_reversed is not None:
        query = query.filter(Offset.is_reversed == is_reversed)

    total = query.count()
    items = (
        query.order_by(Offset.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total
```

- [ ] **Step 3: Verify imports**

`Session`, `Offset` are already imported/available in `service.py`. No new imports needed.

- [ ] **Step 4: Run lint**

Run: `cd backend && ruff check --fix app/modules/billing/service.py && ruff format app/modules/billing/service.py`
Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/billing/service.py
git commit -m "feat(billing): add list_offsets() service function (P0-4 BE-2)"
```

---

## Task 3: Backend — Add `GET /offsets` endpoint + tests (TDD)

**Closure slice:** Add one GET endpoint to `api.py` + write tests
**Non-closure:** Does NOT modify any other endpoint
**Files:**
- Modify: `backend/app/modules/billing/api.py` (add endpoint before existing `POST /offsets`)
- Create: `backend/tests/test_offset_list.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_offset_list.py`:

```python
"""Tests for GET /api/v1/offsets list endpoint (P0-4)."""
from __future__ import annotations

from uuid import uuid4

import pytest

OFFSETS_URL = "/api/v1/offsets"
BILLS_URL = "/api/v1/bills"


# ── Helpers (reused from test_b5_billing_polish.py pattern) ──────────────

def _create_client(client, auth_headers) -> dict:
    payload = {
        "name_cn": f"测试客户-{uuid4().hex[:6]}",
        "short_code": f"TC{uuid4().hex[:4].upper()}",
        "client_type": "COMPANY",
    }
    resp = client.post("/api/v1/clients", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(client, auth_headers, client_id: str) -> dict:
    payload = {
        "case_no": f"CASE-OFF-{uuid4().hex[:6]}",
        "client_id": client_id,
        "case_type": "INVENTION",
        "filing_type": "NEW",
    }
    resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_fee_rate(client, auth_headers, default_amount: str = "1000.00") -> dict:
    payload = {
        "fee_code": f"OFF-{uuid4().hex[:6]}",
        "fee_name": "冲销测试费",
        "fee_type": "SERVICE",
        "currency": "CNY",
        "default_amount": default_amount,
    }
    resp = client.post("/api/v1/fees/rates", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_fee_draft(client, auth_headers, case_id: str, client_id: str) -> dict:
    payload = {"case_id": case_id, "client_id": client_id, "draft_type": "STANDARD"}
    resp = client.post("/api/v1/fees/drafts", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _add_fee_item(client, auth_headers, draft_id: str, rate_id: str, unit_price: str) -> dict:
    payload = {
        "fee_rate_id": rate_id,
        "quantity": 1,
        "unit_price": unit_price,
    }
    resp = client.post(f"/api/v1/fees/drafts/{draft_id}/items", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_bill_from_drafts(client, auth_headers, draft_ids: list[str]) -> dict:
    resp = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": draft_ids},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_payment(client, auth_headers, client_id: str, amount: str) -> dict:
    payload = {
        "client_id": client_id,
        "amount": amount,
        "pay_date": "2026-03-20",
        "currency": "CNY",
    }
    resp = client.post("/api/v1/payments", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _get_payment_line_id(client, auth_headers, payment_id: str) -> str:
    resp = client.get(f"/api/v1/payments/{payment_id}", headers=auth_headers)
    assert resp.status_code == 200
    lines = resp.json().get("lines") or resp.json().get("payment_lines", [])
    assert len(lines) > 0, "No payment lines found"
    return lines[0]["id"]


def _create_offset(client, auth_headers, payment_line_id: str, bill_id: str, amount: str) -> dict:
    payload = {
        "payment_line_id": payment_line_id,
        "bill_id": bill_id,
        "offset_amt": amount,
        "offset_date": "2026-03-20",
    }
    resp = client.post(OFFSETS_URL, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Offset creation failed: {resp.text}"
    return resp.json()


def _setup_billing_chain(client, auth_headers, fee_amount: str = "1000.00") -> dict:
    """Create client → case → rate → draft → item → bill → payment → offset."""
    cl = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=cl["id"])
    rate = _create_fee_rate(client, auth_headers, default_amount=fee_amount)
    draft = _create_fee_draft(client, auth_headers, case["id"], cl["id"])
    _add_fee_item(client, auth_headers, draft["id"], rate["id"], unit_price=fee_amount)
    bill = _create_bill_from_drafts(client, auth_headers, [draft["id"]])
    payment = _create_payment(client, auth_headers, cl["id"], fee_amount)
    payment_line_id = _get_payment_line_id(client, auth_headers, payment["id"])
    offset = _create_offset(client, auth_headers, payment_line_id, bill["id"], fee_amount)
    return {"client": cl, "case": case, "bill": bill, "offset": offset}


# ── Tests ────────────────────────────────────────────────────────────────

def test_list_offsets_empty(client, auth_headers):
    """GET /offsets returns paginated result (may include offsets from other tests)."""
    resp = client.get(OFFSETS_URL, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert isinstance(data["items"], list)


def test_list_offsets_with_data(client, auth_headers):
    """GET /offsets returns offset with enriched bill_no."""
    chain = _setup_billing_chain(client, auth_headers)
    offset_id = chain["offset"]["id"]
    bill_id = chain["bill"]["id"]

    resp = client.get(OFFSETS_URL, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    # Find our offset in the list
    our_offset = next((o for o in data["items"] if o["id"] == offset_id), None)
    assert our_offset is not None, f"Offset {offset_id} not found in list"

    # Verify enriched fields
    assert our_offset["bill_id"] == bill_id
    assert our_offset["bill_no"] is not None  # Enriched from Bill join
    assert "offset_amt" in our_offset
    assert "is_reversed" in our_offset
    assert our_offset["is_reversed"] is False
    assert "created_at" in our_offset


def test_list_offsets_filter_by_bill_id(client, auth_headers):
    """GET /offsets?bill_id=X returns only offsets for that bill."""
    chain = _setup_billing_chain(client, auth_headers)
    bill_id = chain["bill"]["id"]
    offset_id = chain["offset"]["id"]

    resp = client.get(OFFSETS_URL, params={"bill_id": bill_id}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["total"] >= 1
    assert all(o["bill_id"] == bill_id for o in data["items"])
    assert any(o["id"] == offset_id for o in data["items"])


def test_list_offsets_filter_by_is_reversed(client, auth_headers):
    """GET /offsets?is_reversed=false returns only non-reversed offsets."""
    chain = _setup_billing_chain(client, auth_headers)

    # Filter non-reversed
    resp = client.get(OFFSETS_URL, params={"is_reversed": False}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all(o["is_reversed"] is False for o in data["items"])

    # Reverse the offset
    client.post(f"{OFFSETS_URL}/{chain['offset']['id']}/reverse", headers=auth_headers)

    # Filter reversed
    resp = client.get(OFFSETS_URL, params={"is_reversed": True}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    reversed_ids = [o["id"] for o in data["items"]]
    assert chain["offset"]["id"] in reversed_ids


def test_list_offsets_pagination(client, auth_headers):
    """GET /offsets?page=1&page_size=1 returns paginated results."""
    _setup_billing_chain(client, auth_headers)

    resp = client.get(OFFSETS_URL, params={"page": 1, "page_size": 1}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert len(data["items"]) <= 1


def test_list_offsets_unauthorized(client):
    """GET /offsets without auth returns 401."""
    resp = client.get(OFFSETS_URL)
    assert resp.status_code == 401
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_offset_list.py -v`
Expected: FAIL — `GET /offsets` returns 405 Method Not Allowed (endpoint doesn't exist yet)

- [ ] **Step 3: Add endpoint to api.py**

Add the following to `backend/app/modules/billing/api.py`, before the existing `POST /offsets` endpoint (~line 439). Add the import of `list_offsets` and `OffsetListItemResponse`:

Update the import block (add `OffsetListItemResponse` to schema imports, add `list_offsets` to service imports):

```python
# In schema imports, add:
OffsetListItemResponse,

# In service imports, add:
from app.modules.billing.service import (
    list_offsets as list_offsets_service,
)
```

Add the endpoint:

```python
@router.get(
    "/offsets",
    summary="List offsets with optional filters",
)
def list_offsets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    bill_id: str | None = Query(None),
    is_reversed: bool | None = Query(None),
    _perm: None = Depends(require_perm("Bill.Read")),
    db: Session = Depends(get_db),
) -> dict:
    """
    List offsets with pagination and optional filters.

    **Auth**: Bearer JWT
    **Permission**: Bill.Read
    **Query params**: page, page_size, bill_id, is_reversed
    **Curl example**:
    ```bash
    curl -s http://localhost:8000/api/v1/offsets?page=1&page_size=20 \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Paginated offset list
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    """
    items, total = list_offsets_service(
        db,
        page=page,
        page_size=page_size,
        bill_id=bill_id,
        is_reversed=is_reversed,
    )

    # Resolve bill_no for each offset
    bill_ids = {o.bill_id for o in items}
    bill_no_map: dict[str, str | None] = {}
    if bill_ids:
        bills = db.query(Bill.id, Bill.bill_no).filter(Bill.id.in_(bill_ids)).all()
        bill_no_map = {b.id: b.bill_no for b in bills}

    return {
        "items": [
            OffsetListItemResponse(
                id=o.id,
                payment_line_id=o.payment_line_id,
                bill_id=o.bill_id,
                bill_no=bill_no_map.get(o.bill_id),
                offset_amt=o.offset_amt,
                offset_date=o.offset_date,
                is_reversed=o.is_reversed,
                reversed_at=o.reversed_at.isoformat() if o.reversed_at else None,
                created_at=o.created_at.isoformat() if o.created_at else None,
            ).model_dump()
            for o in items
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }
```

Ensure `Query` is imported from `fastapi` (check existing imports — it's likely already there).

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_offset_list.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Run full test suite**

Run: `cd backend && python -m pytest --tb=short`
Expected: All tests pass (no regressions)

- [ ] **Step 6: Run lint**

Run: `cd backend && ruff check --fix . && ruff format .`
Expected: No errors

- [ ] **Step 7: Commit**

```bash
git add backend/app/modules/billing/api.py backend/tests/test_offset_list.py
git commit -m "feat(billing): add GET /offsets list endpoint with tests (P0-4 BE-3)"
```

---

## Task 4: Frontend — Update `OffsetListItem` type

**Closure slice:** Add `bill_no` field to `OffsetListItem` interface
**Non-closure:** Does NOT modify API client functions
**Files:**
- Modify: `frontend/src/api/billing.types.ts:145-155`

- [ ] **Step 1: Add `bill_no` field**

In `frontend/src/api/billing.types.ts`, update the `OffsetListItem` interface (line 145):

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

- [ ] **Step 2: Run typecheck**

Run: `cd frontend && npx vue-tsc --noEmit`
Expected: No errors (new optional field is backward-compatible)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api/billing.types.ts
git commit -m "feat(billing): add bill_no to OffsetListItem type (P0-4 FE-1)"
```

---

## Task 5: Frontend — Update API client (`billing.ts`)

**Closure slice:** Update `BackendOffset`, `mapOffset`, replace `getOffsets` stub
**Non-closure:** Does NOT create page components
**Files:**
- Modify: `frontend/src/api/billing.ts` (lines 88-96, 187-199, 328-340)

- [ ] **Step 1: Update `BackendOffset` interface (line 88)**

Replace:
```typescript
interface BackendOffset {
    id: string
    payment_line_id: string
    bill_id: string
    offset_amt: string | number
    offset_date?: string | null
    is_reversed: boolean
    reversed_at?: string | null
}
```

With:
```typescript
interface BackendOffset {
    id: string
    payment_line_id: string
    bill_id: string
    bill_no?: string | null
    offset_amt: string | number
    offset_date?: string | null
    is_reversed: boolean
    reversed_at?: string | null
    created_at?: string | null
}
```

- [ ] **Step 2: Update `mapOffset` function (line 187)**

Replace:
```typescript
function mapOffset(input: BackendOffset): OffsetListItem {
    return {
        id: input.id,
        payment_line_id: input.payment_line_id,
        bill_id: input.bill_id,
        amount: asNumber(input.offset_amt),
        currency: 'CNY',
        offset_date: input.offset_date || undefined,
        is_reversed: input.is_reversed,
        reversed_at: input.reversed_at || undefined,
        created_at: input.offset_date || '',
    }
}
```

With:
```typescript
function mapOffset(input: BackendOffset): OffsetListItem {
    return {
        id: input.id,
        payment_line_id: input.payment_line_id,
        bill_id: input.bill_id,
        bill_no: input.bill_no || undefined,
        amount: asNumber(input.offset_amt),
        currency: 'CNY',
        offset_date: input.offset_date || undefined,
        is_reversed: input.is_reversed,
        reversed_at: input.reversed_at || undefined,
        created_at: input.created_at || input.offset_date || '',
    }
}
```

- [ ] **Step 3: Replace `getOffsets` stub (line 328)**

Replace:
```typescript
export async function getOffsets(
    params: { page?: number; page_size?: number; bill_id?: string } = {}
): Promise<Pagination<OffsetListItem>> {
    const page = params.page || 1
    const pageSize = params.page_size || 20

    return {
        items: [],
        page,
        page_size: pageSize,
        total: 0,
    }
}
```

With:
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

- [ ] **Step 4: Run typecheck + lint**

Run: `cd frontend && npx vue-tsc --noEmit && npm run lint`
Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/billing.ts
git commit -m "feat(billing): wire getOffsets to real API, update BackendOffset+mapOffset (P0-4 FE-2)"
```

---

## Task 6: Frontend — Create `OffsetList.vue` page

**Closure slice:** Create one new Vue page component
**Non-closure:** Does NOT modify router or menu
**Files:**
- Create: `frontend/src/modules/billing/pages/OffsetList.vue`

- [ ] **Step 1: Create `OffsetList.vue`**

Create `frontend/src/modules/billing/pages/OffsetList.vue`:

```vue
<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h2>冲销管理</h2>
      </div>
      <div class="page-header-right">
        <el-button @click="fetchData" :loading="loading">刷新</el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <el-alert :title="String(error)" type="error" show-icon closable @close="error = null" />
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar" style="margin-bottom: 16px; display: flex; gap: 12px; align-items: center;">
      <el-select v-model="filterReversed" placeholder="反转状态" clearable style="width: 140px;" @change="handleFilter">
        <el-option label="全部" value="" />
        <el-option label="正常" :value="false" />
        <el-option label="已反转" :value="true" />
      </el-select>
      <el-button type="primary" @click="handleFilter">查询</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>

    <!-- Table -->
    <el-table
      v-loading="loading"
      :data="items"
      stripe
      size="small"
      class="compact-table"
    >
      <el-table-column label="冲销金额" width="140" align="right">
        <template #default="{ row }">
          <span class="mono-num">{{ formatAmount(row.amount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="冲销日期" width="130">
        <template #default="{ row }">
          {{ row.offset_date || '—' }}
        </template>
      </el-table-column>
      <el-table-column label="账单号" width="160">
        <template #default="{ row }">
          <el-link type="primary" @click="goToBill(row.bill_id)">
            {{ row.bill_no || row.bill_id.slice(0, 8) }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.is_reversed" type="danger" size="small">已反转</el-tag>
          <el-tag v-else type="success" size="small">正常</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="反转时间" width="160">
        <template #default="{ row }">
          {{ row.reversed_at || '—' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button
            v-if="!row.is_reversed"
            type="danger"
            size="small"
            text
            @click="handleReverse(row)"
          >
            反转
          </el-button>
          <span v-else class="text-muted">—</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchData"
        @size-change="fetchData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOffsets, reverseOffset } from '../../../api/billing'
import type { OffsetListItem } from '../../../api/billing.types'

const router = useRouter()

const items = ref<OffsetListItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterReversed = ref<boolean | string>('')

function formatAmount(val: number): string {
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function fetchData() {
  loading.value = true
  error.value = null
  try {
    const params: Record<string, unknown> = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filterReversed.value !== '' && filterReversed.value !== null) {
      params.is_reversed = filterReversed.value
    }
    const result = await getOffsets(params as Parameters<typeof getOffsets>[0])
    items.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = String(err)
  } finally {
    loading.value = false
  }
}

function handleFilter() {
  page.value = 1
  fetchData()
}

function handleReset() {
  filterReversed.value = ''
  page.value = 1
  fetchData()
}

async function handleReverse(row: OffsetListItem) {
  const billLabel = row.bill_no || row.bill_id.slice(0, 8)
  const amountLabel = formatAmount(row.amount)

  try {
    await ElMessageBox.confirm(
      `冲销金额：¥${amountLabel}\n关联账单：${billLabel}\n\n反转后，账单余额将恢复，付款行可用金额将增加。此操作不可撤销。`,
      '确认反转冲销',
      {
        confirmButtonText: '确认反转',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
    await reverseOffset(row.id)
    ElMessage.success('冲销已反转')
    await fetchData()
  } catch {
    // User cancelled or API error — silently ignore cancel
  }
}

function goToBill(billId: string) {
  router.push({ name: 'bill_detail', params: { id: billId } })
}

onMounted(fetchData)
</script>
```

- [ ] **Step 2: Run typecheck + lint**

Run: `cd frontend && npx vue-tsc --noEmit && npm run lint`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/modules/billing/pages/OffsetList.vue
git commit -m "feat(billing): add OffsetList.vue page component (P0-4 FE-3)"
```

---

## Task 7: Frontend — Add route for OffsetList

**Closure slice:** Add one route entry to `router/index.ts`
**Non-closure:** Does NOT modify menu
**Files:**
- Modify: `frontend/src/router/index.ts` (add after `billing/payments` route, ~line 71)

- [ ] **Step 1: Add route**

In `frontend/src/router/index.ts`, add after the `payments` route (line 71):

```typescript
{ path: 'billing/offsets', name: 'offsets', component: () => import('../modules/billing/pages/OffsetList.vue') },
```

- [ ] **Step 2: Run typecheck**

Run: `cd frontend && npx vue-tsc --noEmit`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/router/index.ts
git commit -m "feat(billing): add /billing/offsets route (P0-4 FE-4)"
```

---

## Task 8: Frontend — Add menu entry

**Closure slice:** Add one menu item to `menu.ts`
**Non-closure:** Does NOT modify any other file
**Files:**
- Modify: `frontend/src/constants/menu.ts` (add in `finance` group after `payments`)

- [ ] **Step 1: Add menu item**

In `frontend/src/constants/menu.ts`, in the `finance` children array, add after the `payments` entry (after line 56):

```typescript
{ key: 'offsets', label: '冲销管理', icon: '🔄', route: '/billing/offsets', requiredPerms: [Perms.BILLING_READ] },
```

- [ ] **Step 2: Run lint + typecheck**

Run: `cd frontend && npm run lint && npx vue-tsc --noEmit`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/constants/menu.ts
git commit -m "feat(billing): add 冲销管理 menu entry (P0-4 FE-5)"
```

---

## Task 9: Final verification gate

**Closure slice:** Run all quality gates, verify acceptance criteria
**Non-closure:** Does NOT modify any code
**Files:** None (read-only verification)

- [ ] **Step 1: Backend full test suite**

Run: `cd backend && python -m pytest --tb=short`
Expected: All tests pass

- [ ] **Step 2: Frontend quality gate**

Run: `cd frontend && npm run lint && npm run typecheck && npm run build`
Expected: All pass with zero errors

- [ ] **Step 3: SQLite clean rebuild test**

Run: `cd backend && rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py`
Expected: No errors

- [ ] **Step 4: Generate evidence artifacts**

Create `artifacts/P0-4/` directory and generate:
- `summary.md` — acceptance criteria checklist with PASS/FAIL
- `results.jsonl` — verification command results
- `git/diff.patch` — scoped diff for all P0-4 commits

---

## Dependency Graph

```
Task 1 (schema) ──→ Task 2 (service) ──→ Task 3 (endpoint+tests)
                                                    │
                                                    ▼
                                         Task 4 (FE types) ──→ Task 5 (API client)
                                                                       │
                                                                       ▼
                                                            Task 6 (OffsetList.vue)
                                                                       │
                                                                       ▼
                                                            Task 7 (route) ──→ Task 8 (menu)
                                                                                      │
                                                                                      ▼
                                                                           Task 9 (verification)
```
