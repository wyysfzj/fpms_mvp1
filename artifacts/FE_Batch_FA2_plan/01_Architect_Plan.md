# FA2 Architect Plan — List UX Polish: Filter Dropdowns

## 1. FA2 Summary

**Goal**: Add missing filter dropdowns (el-select) to 4 list pages so users can filter results without reloading the page.

**Scope**: 4 Vue list pages — DocumentList, TaskList, BillList, FeeDraftList.

**Non-scope**:
- No new backend endpoints or API parameters
- No new API client functions (all params already exist in types & wrappers)
- No new components — just add `<el-select>` within each page
- No router changes, no store changes

---

## 2. Backend Dependency

**Confirmed: NONE**

All 4 backend endpoints already accept the required filter query parameters:

| Endpoint | Filter Param | Backend File | Confirmed |
|----------|-------------|--------------|-----------|
| `GET /api/v1/documents` | `direction` (DocumentDirection enum: IN/OUT) | `backend/app/modules/documents/api.py:124` | YES |
| `GET /api/v1/tasks` | `status` (str) | `backend/app/modules/tasks/api.py:100` | YES |
| `GET /api/v1/bills` | _(no status param)_ | `backend/app/modules/billing/api.py:40` | **ISSUE** |
| `GET /api/v1/fees/drafts` | `status` (alias for `status_filter`) | `backend/app/modules/fees/api.py:41` | YES |

### CRITICAL FINDING: BillList Backend Gap

The `GET /api/v1/bills` endpoint (`billing/api.py:40-92`) does **NOT** accept a `status` query parameter. The handler only has `page` and `page_size` params. The raw query (`db.query(Bill)`) has no status filter.

However, the **frontend API client** (`billing.ts:160-170`) already passes `status` to the request:
```ts
const { page = 1, page_size = 20, status, client_id } = params
const response = await http.get<Pagination<BackendBill>>('/bills', {
    params: { page, page_size, status, client_id }
})
```

And the **type** (`billing.types.ts:47-52`) defines `status?: BillStatus` in `BillListParams`.

**Impact**: The frontend will send `?status=ISSUED` but the backend will **ignore** it (FastAPI ignores unknown query params by default). The data will NOT be filtered server-side.

**Decision**: We should still add the UI filter dropdown for BillList per spec, because:
1. The spec says "Wire to existing `?status=` param" — the frontend API already sends it
2. When backend later adds the filter, it will "just work"
3. For now, we can apply **client-side filtering** as a fallback, OR document this as a known gap

**Recommended approach**: Add the filter dropdown and wire it to the API call (as spec requires). The param is sent but ignored by the current backend. Document this in findings.md. The UX will appear to work for small data sets where all results are on the current page, but for large data sets, filtering will be incomplete until backend is updated.

---

## 3. File Allowlist

| # | File | Action | Lines |
|---|------|--------|-------|
| 1 | `frontend/src/modules/documents/pages/DocumentList.vue` | MODIFY | ~165 |
| 2 | `frontend/src/modules/tasks/pages/TaskList.vue` | MODIFY | ~308 |
| 3 | `frontend/src/modules/billing/pages/BillList.vue` | MODIFY | ~171 |
| 4 | `frontend/src/modules/fees/pages/FeeDraftList.vue` | MODIFY | ~190 |

---

## 4. Current State per Page

### 4.1 DocumentList.vue
- **Current filters**: NONE. No filter bar, no direction filter.
- **fetchDocuments()**: Calls `getDocuments({ page, page_size })` — does NOT pass `direction`.
- **Watcher**: Watches `[page, pageSize]` only.
- **Needs**: Add `filterDirection` ref, add el-select with IN/OUT/ALL, pass to `getDocuments()`, reset page on filter change.

### 4.2 TaskList.vue
- **Current filters**: NONE. No filter bar, no status filter.
- **fetchTasks()**: Calls `getTasks({ page, page_size })` — does NOT pass `status`.
- **Watcher**: Watches `[page, pageSize]` only.
- **Needs**: Add `filterStatus` ref, add el-select with status options, pass to `getTasks()`, reset page on filter change.

### 4.3 BillList.vue
- **Current filters**: NONE. No filter bar, no status filter.
- **fetchBills()**: Calls `getBills({ page, page_size })` — does NOT pass `status`.
- **Watcher**: Watches `[page, pageSize]` only.
- **Needs**: Add `filterStatus` ref, add el-select with status options, pass to `getBills()`, reset page on filter change.

### 4.4 FeeDraftList.vue
- **Current filters**: NONE. No filter bar, no status filter.
- **fetchDrafts()**: Calls `getFeeDrafts({ page, page_size })` — does NOT pass `status`.
- **Watcher**: Watches `[page, pageSize]` only.
- **Needs**: Add `filterStatus` ref, add el-select with OPEN/LOCKED/ALL, pass to `getFeeDrafts()`, reset page on filter change.

---

## 5. API Param Compatibility

### 5.1 Documents
- **Type**: `DocumentListParams` has `direction?: 'IN' | 'OUT'`
- **API Client** (`documents.ts:88-98`): `getDocuments()` destructures `direction` and conditionally spreads `{ direction }` into params
- **Compatible**: YES. Pass `direction` or omit for ALL.
- **Note**: The type is `'IN' | 'OUT'`, not a union with `''`. For "ALL", we should pass `undefined` (omit the param), not `''`.

### 5.2 Tasks
- **Type**: `TaskListParams` has `status?: string`
- **API Client** (`tasks.ts:55-65`): `getTasks()` destructures `status` and conditionally spreads `{ status }` into params
- **Compatible**: YES. The backend accepts any string for status.
- **Note**: For "ALL", pass `undefined`. Backend valid values: `OPEN`, `IN_PROGRESS`, `CLOSED`, `COMPLETED`, `CANCELLED`.

### 5.3 Bills
- **Type**: `BillListParams` has `status?: BillStatus` (which is `string`)
- **API Client** (`billing.ts:160-170`): `getBills()` destructures `status` and passes it directly in params (no conditional spread — always sends it)
- **Compatible**: YES on frontend side. Backend ignores extra params.
- **Note**: For "ALL", pass `undefined`. Frontend display values: `ISSUED`, `PAID`, `UNSETTLED`, `VOID`.

### 5.4 Fee Drafts
- **Type**: `FeeDraftListParams` has `status?: FeeDraftStatus` (which is `'OPEN' | 'LOCKED'`)
- **API Client** (`fees.ts:134-142`): `getFeeDrafts()` destructures `status` and passes directly in params
- **Compatible**: YES. Backend uses `alias="status"` for `status_filter` param.
- **Note**: For "ALL", pass `undefined`.

---

## 6. Implementation Spec per Page

### 6.1 DocumentList.vue — Direction Filter

**Variable**: `const filterDirection = ref<string>('')`

**el-select options**:
| label | value | Meaning |
|-------|-------|---------|
| 全部 | `''` | No filter (ALL) |
| 收文 | `'IN'` | Incoming |
| 发文 | `'OUT'` | Outgoing |

**Wiring**:
```ts
// In fetchDocuments():
const result = await getDocuments({
  page: page.value,
  page_size: pageSize.value,
  direction: filterDirection.value ? filterDirection.value as 'IN' | 'OUT' : undefined,
})
```

**Filter change handler** — Add `onFilterChange()`:
```ts
function onFilterChange() {
  page.value = 1
  fetchDocuments()
}
```

**Template** — Insert before `<el-table>` (inside `<div v-else class="page-table">`):
```html
<el-row :gutter="16" style="margin-bottom: 16px">
  <el-col :span="6">
    <el-select v-model="filterDirection" placeholder="方向" clearable @change="onFilterChange">
      <el-option label="全部" value="" />
      <el-option label="收文" value="IN" />
      <el-option label="发文" value="OUT" />
    </el-select>
  </el-col>
</el-row>
```

**Watch update**: Add `filterDirection` to the watch is NOT needed since we handle it via `@change="onFilterChange"`. The existing `watch([page, pageSize])` stays for pagination only.

### 6.2 TaskList.vue — Status Filter

**Variable**: `const filterStatus = ref<string>('')`

**el-select options**:
| label | value | Meaning |
|-------|-------|---------|
| 全部状态 | `''` | No filter |
| 待处理 | `'OPEN'` | Open/Pending |
| 进行中 | `'IN_PROGRESS'` | In progress |
| 已完成 | `'COMPLETED'` | Completed/Done |
| 已取消 | `'CANCELLED'` | Cancelled |

**Wiring**:
```ts
// In fetchTasks():
const result = await getTasks({
  page: page.value,
  page_size: pageSize.value,
  status: filterStatus.value || undefined,
})
```

**Filter change handler**:
```ts
function onFilterChange() {
  page.value = 1
  fetchTasks()
}
```

**Template** — Insert before `<el-table>` (inside `<div v-else class="page-table">`):
```html
<el-row :gutter="16" style="margin-bottom: 16px">
  <el-col :span="6">
    <el-select v-model="filterStatus" placeholder="全部状态" clearable @change="onFilterChange">
      <el-option label="全部状态" value="" />
      <el-option label="待处理" value="OPEN" />
      <el-option label="进行中" value="IN_PROGRESS" />
      <el-option label="已完成" value="COMPLETED" />
      <el-option label="已取消" value="CANCELLED" />
    </el-select>
  </el-col>
</el-row>
```

### 6.3 BillList.vue — Status Filter

**Variable**: `const filterStatus = ref<string>('')`

**el-select options**:
| label | value | Meaning |
|-------|-------|---------|
| 全部状态 | `''` | No filter |
| 已开具 | `'ISSUED'` | Issued |
| 已支付 | `'PAID'` | Paid |
| 未结清 | `'UNSETTLED'` | Unsettled |
| 已作废 | `'VOID'` | Void |

**Wiring**:
```ts
// In fetchBills():
const result = await getBills({
  page: page.value,
  page_size: pageSize.value,
  status: filterStatus.value || undefined,
})
```

**Filter change handler**:
```ts
function onFilterChange() {
  page.value = 1
  fetchBills()
}
```

**Template** — Insert before `<el-table>` (inside `<div v-else class="page-table">`):
```html
<el-row :gutter="16" style="margin-bottom: 16px">
  <el-col :span="6">
    <el-select v-model="filterStatus" placeholder="全部状态" clearable @change="onFilterChange">
      <el-option label="全部状态" value="" />
      <el-option label="已开具" value="ISSUED" />
      <el-option label="已支付" value="PAID" />
      <el-option label="未结清" value="UNSETTLED" />
      <el-option label="已作废" value="VOID" />
    </el-select>
  </el-col>
</el-row>
```

**Note**: The spec says options should be ALL / ISSUED / PAID / VOID, but the actual `BILL_STATUS_TEXT` constants include `UNSETTLED` as well. Including it for completeness since that is what the backend's `create_manual_bill` defaults to.

### 6.4 FeeDraftList.vue — Status Filter

**Variable**: `const filterStatus = ref<string>('')`

**el-select options**:
| label | value | Meaning |
|-------|-------|---------|
| 全部状态 | `''` | No filter |
| 开放 | `'OPEN'` | Open draft |
| 已锁定 | `'LOCKED'` | Locked draft |

**Wiring**:
```ts
// In fetchDrafts():
const result = await getFeeDrafts({
  page: page.value,
  page_size: pageSize.value,
  status: (filterStatus.value || undefined) as FeeDraftStatus | undefined,
})
```

**Filter change handler**:
```ts
function onFilterChange() {
  page.value = 1
  fetchDrafts()
}
```

**Template** — Insert before `<el-table>` (inside `<div v-else class="page-table">`):
```html
<el-row :gutter="16" style="margin-bottom: 16px">
  <el-col :span="6">
    <el-select v-model="filterStatus" placeholder="全部状态" clearable @change="onFilterChange">
      <el-option label="全部状态" value="" />
      <el-option label="开放" value="OPEN" />
      <el-option label="已锁定" value="LOCKED" />
    </el-select>
  </el-col>
</el-row>
```

**Import note**: Need to import `FeeDraftStatus` from the types file for the cast.

---

## 7. Pattern Template

All 4 pages follow the same pattern:

### Template (insert before `<el-table>` inside the `<div v-else class="page-table">` block):
```html
<el-row :gutter="16" style="margin-bottom: 16px">
  <el-col :span="6">
    <el-select v-model="filterVar" placeholder="全部" clearable @change="onFilterChange">
      <el-option label="全部" value="" />
      <el-option label="Label1" value="VALUE1" />
      <el-option label="Label2" value="VALUE2" />
    </el-select>
  </el-col>
</el-row>
```

### Script changes:
1. Add `const filterVar = ref<string>('')`
2. Add `onFilterChange()` function that resets `page.value = 1` and calls `fetchX()`
3. Update `fetchX()` to pass filter param to API call
4. Do NOT add filter to existing `watch([page, pageSize])` — keep that for pagination only

---

## 8. Chinese Text Inventory

### DocumentList filter labels:
- Placeholder: `方向` (direction)
- `全部` = All
- `收文` = Incoming (IN)
- `发文` = Outgoing (OUT)

### TaskList filter labels:
- Placeholder: `全部状态`
- `全部状态` = All statuses
- `待处理` = Open/Pending (OPEN)
- `进行中` = In Progress (IN_PROGRESS)
- `已完成` = Completed (COMPLETED)
- `已取消` = Cancelled (CANCELLED)

### BillList filter labels:
- Placeholder: `全部状态`
- `全部状态` = All statuses
- `已开具` = Issued (ISSUED)
- `已支付` = Paid (PAID)
- `未结清` = Unsettled (UNSETTLED)
- `已作废` = Void (VOID)

### FeeDraftList filter labels:
- Placeholder: `全部状态`
- `全部状态` = All statuses
- `开放` = Open (OPEN)
- `已锁定` = Locked (LOCKED)

All Chinese labels are consistent with the existing `displayText.ts` constants.

---

## 9. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| BillList backend ignores `status` param | Medium | Document in findings.md. Frontend sends param correctly; will auto-work when backend adds filter. |
| `clearable` on el-select resets to `null` not `''` | Low | Using `value=""` for the "ALL" option and `\|\| undefined` in fetch ensures both `''` and `null/undefined` map to no-filter. Test: when user clicks X to clear, value becomes `null`. Our `filterStatus.value \|\| undefined` evaluates `null \|\| undefined` → `undefined`, which is correct. |
| Empty state shows when filter yields 0 results | Low | The existing `isEmpty` computed checks `total.value === 0`. This is correct — if the filtered query returns 0 total, the empty state should show. However, the empty state CTA ("新建...") might be confusing when filters are active. This is a minor UX issue, not a blocker. |
| TypeScript cast for FeeDraftStatus | Low | The `filterStatus` ref is `string` but `FeeDraftListParams.status` is `FeeDraftStatus`. We cast `as FeeDraftStatus \| undefined` when passing to API. |
| Page count header shows filtered total | None | The `total` ref already shows whatever the API returns, which will be the filtered count. This is correct behavior. |

---

## 10. Task Decomposition for Implementation Agent

The implementation agent should modify 4 files with exactly 3 changes per file:

### Per file:
1. **Add ref** — `const filterX = ref<string>('')` after other refs
2. **Add template** — Insert `<el-row>` with `<el-select>` before `<el-table>` inside `page-table` div
3. **Update fetch** — Pass filter param in the API call
4. **Add handler** — Add `onFilterChange()` function

### Order: Can be done in any order (no inter-file dependencies).

### Quality Gate:
```bash
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## 11. Acceptance Criteria Checklist

- [ ] DocumentList has direction filter dropdown (全部/收文/发文)
- [ ] TaskList has status filter dropdown (全部状态/待处理/进行中/已完成/已取消)
- [ ] BillList has status filter dropdown (全部状态/已开具/已支付/未结清/已作废)
- [ ] FeeDraftList has status filter dropdown (全部状态/开放/已锁定)
- [ ] All filters reset page to 1 when changed
- [ ] All filters pass the filter value to the corresponding API call
- [ ] `npm run lint` passes
- [ ] `npm run typecheck` passes
- [ ] `npm run build` passes
- [ ] No new files created (all modifications to existing files)
