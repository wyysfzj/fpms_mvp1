# FB5 — Case Advanced Search Filter Panel: Execution Plan

**Batch**: FB5
**Author**: Architect Agent
**Date**: 2026-02-27
**Status**: READY FOR IMPLEMENTATION

---

## 1. Scope Summary

Add a collapsible filter panel to CaseList.vue with 8 server-side filter parameters. The backend (A5) already supports all 8 filters on `GET /api/v1/cases`. The frontend currently sends only `page` and `page_size`.

---

## 2. CaseListParams Issue — Resolution

### Problem
`CaseListParams` is defined in `cases.types.ts` (line 57-60) with only `page` and `page_size`. Adding 8 filter fields requires modifying this interface, but `cases.types.ts` is NOT in the FB5 file allowlist.

### Recommendation: **Option B — Extend inline in `cases.ts`**
Define a new `CaseFilterParams` interface directly in `cases.ts` that extends `CaseListParams`:

```typescript
/** FB5: Filter parameters for getCases() — extends base pagination */
interface CaseFilterParams extends CaseListParams {
  client_id?: string
  case_type?: string
  patent_category?: string
  flow_dir?: string
  status?: string
  filing_date_from?: string
  filing_date_to?: string
  primary_agent_id?: string
}
```

**Rationale**:
- Stays within the strict 2-file allowlist (`cases.ts`, `CaseList.vue`)
- `CaseListParams` is already imported by `cases.ts` (line 3), so extending it is natural
- No scope deviation needed — no team lead approval required
- `CaseFilterParams` is private to `cases.ts` (not exported), keeping the interface surface clean
- The original `getCases(params: CaseListParams)` signature changes to `getCases(params: CaseFilterParams)` but remains backward-compatible since all new fields are optional

**Alternative (Option A)**: Add `cases.types.ts` to allowlist. Cleaner long-term, but requires scope deviation approval. Can be done as a follow-up cleanup task.

---

## 3. Verified Enum Values (from Backend)

### 3a. CaseType (`backend/app/modules/cases/enums.py:6-12`)
| Value | Chinese Label |
|-------|--------------|
| `NORMAL` | 普通申请 |
| `PCT_INTL` | PCT国际 |
| `PCT_NATL` | PCT国内 |
| `PRIORITY` | 优先权 |

### 3b. PatentCategory (`enums.py:23-28`)
| Value | Chinese Label |
|-------|--------------|
| `INV` | 发明 |
| `UM` | 实用新型 |
| `DES` | 外观设计 |

> **NOTE**: Backend enum uses `UM` (not `UTL` as in spec). Frontend must use `UM`.

### 3c. FlowDir (`enums.py:15-20`)
| Value | Chinese Label |
|-------|--------------|
| `CN_DOMESTIC` | 国内 |
| `CN_OUTBOUND` | 出境 |
| `FOREIGN_INBOUND` | 入境 |

> **NOTE**: Backend enum values differ from spec (no `PCT_IN`, `PCT_OUT`, `PARIS_IN`, `PARIS_OUT`). Must use actual backend values.

### 3d. CaseStatus (`enums.py:31-54` + `displayText.ts:1-17`)
All status values with Chinese labels from `CASE_STATUS_TEXT`:
| Value | Label |
|-------|-------|
| `NOT_FILED` | 未递交 |
| `WAITING_RECEIPT` | 等待受理 |
| `PRELIM_EXAM` | 初审 |
| `AMENDMENT` | 补正中 |
| `PRELIM_PASS` | 初审通过 |
| `PUBLISHED` | 已公开 |
| `SUB_EXAM` | 实审中 |
| `OA1` | 一通阶段 |
| `OA2` | 二通阶段 |
| `GRANTED` | 已授权 |
| `REJECTED` | 驳回 |
| `TERMINATED` | 中止/终止 |
| `INVALIDATED` | 全部无效 |
| `INVALIDATED_PARTIAL` | 部分无效 |
| `REEXAM` | 复审中 |
| `PENDING` | 审查中 (legacy) |
| `WITHDRAWN` | 已撤回 (legacy) |
| `ABANDONED` | 已放弃 (legacy) |
| `EXPIRED` | 已到期 (legacy) |

For the filter dropdown, use the 15 workflow-era statuses from `CASE_STATUS_TEXT` (exclude legacy values without display text).

---

## 4. File-by-File Change Spec

### 4a. `frontend/src/api/cases.ts` (T1)

**Current state**: 151 lines. `getCases()` destructures only `{ page, page_size }`.

**Changes**:

1. **Add `CaseFilterParams` interface** (after line 3, before `BackendCase` interface):
```typescript
/** FB5: Server-side filter parameters for case list */
interface CaseFilterParams extends CaseListParams {
  client_id?: string
  case_type?: string
  patent_category?: string
  flow_dir?: string
  status?: string
  filing_date_from?: string   // YYYY-MM-DD
  filing_date_to?: string     // YYYY-MM-DD
  primary_agent_id?: string
}
```

2. **Update `getCases()` function** (lines 85-95):
```typescript
export async function getCases(params: CaseFilterParams = {}): Promise<Pagination<Case>> {
    const { page = 1, page_size = 20, ...filters } = params
    // Build clean params object — only include non-empty filter values
    const queryParams: Record<string, string | number> = { page, page_size }
    for (const [key, value] of Object.entries(filters)) {
        if (value !== undefined && value !== null && value !== '') {
            queryParams[key] = value
        }
    }
    const response = await http.get<Pagination<BackendCase>>('/cases', {
        params: queryParams
    })

    return {
        ...response.data,
        items: response.data.items.map(mapCase),
    }
}
```

**Key design decisions**:
- Use rest spread `...filters` to forward all filter params dynamically
- Strip empty/null/undefined values to keep the URL clean
- Backward-compatible: existing callers passing `{ page, page_size }` still work

### 4b. `frontend/src/modules/cases/pages/CaseList.vue` (T2)

**Current state**: 202 lines. Has `stepFilter` (client-side route query filter), pagination, table.

**Changes**:

#### Template section — Add filter panel (insert between `page-header` div and filter-subtitle div):

```html
<!-- FB5: Advanced Filter Panel -->
<el-card class="filter-panel" shadow="never" style="margin-bottom: 16px;">
  <el-row :gutter="16">
    <el-col :span="6">
      <el-form-item label="客户" class="filter-item">
        <el-select
          v-model="filters.client_id"
          placeholder="全部客户"
          clearable
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="c in clientOptions"
            :key="c.id"
            :label="c.name"
            :value="c.id"
          />
        </el-select>
      </el-form-item>
    </el-col>
    <el-col :span="6">
      <el-form-item label="案件类型" class="filter-item">
        <el-select v-model="filters.case_type" placeholder="全部" clearable style="width: 100%">
          <el-option label="普通申请" value="NORMAL" />
          <el-option label="PCT国际" value="PCT_INTL" />
          <el-option label="PCT国内" value="PCT_NATL" />
          <el-option label="优先权" value="PRIORITY" />
        </el-select>
      </el-form-item>
    </el-col>
    <el-col :span="6">
      <el-form-item label="专利类别" class="filter-item">
        <el-select v-model="filters.patent_category" placeholder="全部" clearable style="width: 100%">
          <el-option label="发明" value="INV" />
          <el-option label="实用新型" value="UM" />
          <el-option label="外观设计" value="DES" />
        </el-select>
      </el-form-item>
    </el-col>
    <el-col :span="6">
      <el-form-item label="流向" class="filter-item">
        <el-select v-model="filters.flow_dir" placeholder="全部" clearable style="width: 100%">
          <el-option label="国内" value="CN_DOMESTIC" />
          <el-option label="出境" value="CN_OUTBOUND" />
          <el-option label="入境" value="FOREIGN_INBOUND" />
        </el-select>
      </el-form-item>
    </el-col>
  </el-row>
  <el-row :gutter="16">
    <el-col :span="6">
      <el-form-item label="状态" class="filter-item">
        <el-select v-model="filters.status" placeholder="全部" clearable style="width: 100%">
          <el-option
            v-for="(label, key) in statusOptions"
            :key="key"
            :label="label"
            :value="key"
          />
        </el-select>
      </el-form-item>
    </el-col>
    <el-col :span="6">
      <el-form-item label="申请日从" class="filter-item">
        <el-date-picker
          v-model="filters.filing_date_from"
          type="date"
          placeholder="起始日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
    </el-col>
    <el-col :span="6">
      <el-form-item label="申请日至" class="filter-item">
        <el-date-picker
          v-model="filters.filing_date_to"
          type="date"
          placeholder="截止日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
    </el-col>
    <el-col :span="6">
      <el-form-item label="主办代理人" class="filter-item">
        <el-input
          v-model="filters.primary_agent_id"
          placeholder="请输入代理人ID"
          clearable
        />
      </el-form-item>
    </el-col>
  </el-row>
  <el-row justify="end">
    <el-button type="primary" @click="handleSearch">搜索</el-button>
    <el-button @click="handleResetFilters">重置</el-button>
  </el-row>
</el-card>
```

#### Script section — New imports and reactive state:

**New imports** (add alongside existing):
```typescript
import { getClients } from '../../../api/clients'
import type { Client } from '../../../api/clients.types'
import { CASE_STATUS_TEXT } from '../../../constants/displayText'
```

**New reactive state**:
```typescript
// FB5: Filter state
const filters = reactive({
  client_id: '',
  case_type: '',
  patent_category: '',
  flow_dir: '',
  status: '',
  filing_date_from: '',
  filing_date_to: '',
  primary_agent_id: '',
})

// Client options for selector
const clientOptions = ref<Array<{ id: string; name: string }>>([])

// Status options (from displayText.ts)
const statusOptions = CASE_STATUS_TEXT
```

**New functions**:
```typescript
/** FB5: Load client options for filter dropdown */
async function fetchClientOptions() {
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clientOptions.value = result.items.map(c => ({ id: c.id, name: c.name }))
  } catch {
    // Silently fail — client filter will just be empty
  }
}

/** FB5: Trigger filtered search — resets to page 1 */
function handleSearch() {
  page.value = 1
  fetchCases()
}

/** FB5: Reset all filter fields and re-fetch */
function handleResetFilters() {
  filters.client_id = ''
  filters.case_type = ''
  filters.patent_category = ''
  filters.flow_dir = ''
  filters.status = ''
  filters.filing_date_from = ''
  filters.filing_date_to = ''
  filters.primary_agent_id = ''
  page.value = 1
  fetchCases()
}
```

**Modify `fetchCases()`** — pass filters to API:
```typescript
async function fetchCases() {
  loading.value = true
  error.value = null
  try {
    const result = await getCases({
      page: page.value,
      page_size: stepFilter.value ? 200 : pageSize.value,
      // FB5: pass active filter values
      ...filters,
    })
    cases.value = result.items
    if (stepFilter.value) {
      total.value = displayCases.value.length
    } else {
      total.value = result.total
    }
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}
```

**Modify `onMounted`** — also load client options:
```typescript
onMounted(() => {
  fetchCases()
  fetchClientOptions()
})
```

#### Style section — Add filter panel styles:
```css
.filter-panel {
  border: 1px solid var(--color-border);
}
.filter-panel .filter-item {
  margin-bottom: 8px;
}
.filter-panel .filter-item :deep(.el-form-item__label) {
  font-size: 12px;
  color: var(--text-sub);
  padding-bottom: 2px;
}
```

---

## 5. Interaction Flow

### 5a. Search Button Click
1. User fills in any combination of the 8 filters
2. Clicks "搜索"
3. `handleSearch()` resets `page.value = 1`, calls `fetchCases()`
4. `fetchCases()` spreads `...filters` into `getCases()` params
5. `getCases()` strips empty values, sends only non-empty params to backend
6. Backend applies server-side filtering, returns paginated results
7. UI updates table and pagination

### 5b. Reset Button Click
1. User clicks "重置"
2. `handleResetFilters()` clears all 8 filter fields to `''`
3. Resets page to 1, calls `fetchCases()`
4. `getCases()` strips empty strings → sends only `page` and `page_size`
5. Full unfiltered list displayed

### 5c. Pagination After Filter
- Watch on `[page, pageSize]` already calls `fetchCases()`
- Since `filters` is part of the `getCases()` params, pagination naturally preserves active filters

---

## 6. Integration with Existing `stepFilter`

### Current Behavior
- `stepFilter` comes from `route.query.step` (set by Dashboard workflow panel)
- When active: fetches 200 items, then filters client-side via `displayCases` computed
- "清除阶段筛选" button removes the `step` query param

### Coexistence Strategy
- **Both can be active simultaneously**: server-side filters reduce the API result set, `stepFilter` further narrows client-side
- `stepFilter` operates on the `displayCases` computed which runs AFTER server-side filtering
- Example: User selects `client_id=X` in filter panel + arrives via `?step=PUBLISHED` → API returns X's cases, then `displayCases` shows only those in PUBLISHED step
- The `page_size: 200` override when `stepFilter` is active continues to work as before
- No conflicts because:
  - Server-side filters go to API as query params
  - `stepFilter` is a route query param that drives client-side computed filtering
  - They are additive/AND behavior

### Edge Case
- If user has `stepFilter` active AND uses the `status` filter in the panel, both apply. The backend filters by `status`, then `displayCases` further filters by `stepKey`. This is consistent — not contradictory — since `status` and `stepKey` are related but different (multiple statuses map to one step).

---

## 7. Acceptance Criteria Checklist

| # | Criterion | Verification |
|---|-----------|-------------|
| AC-1 | Filter panel visible on CaseList page with 8 filter controls | Visual inspection |
| AC-2 | Client dropdown loads from `getClients()` with filterable search | Click dropdown, type to filter |
| AC-3 | Case type dropdown has 4 options matching backend enum | Check values: NORMAL, PCT_INTL, PCT_NATL, PRIORITY |
| AC-4 | Patent category dropdown has 3 options: INV, UM, DES | Verify labels and values |
| AC-5 | Flow direction dropdown has 3 options matching backend enum | Verify: CN_DOMESTIC, CN_OUTBOUND, FOREIGN_INBOUND |
| AC-6 | Status dropdown shows all 15 status labels from CASE_STATUS_TEXT | Verify dropdown list |
| AC-7 | Date pickers format as YYYY-MM-DD | Select date, inspect API call |
| AC-8 | Agent ID is free text input | Type and verify |
| AC-9 | "搜索" button resets page to 1 and fetches with filters | Click search, check network |
| AC-10 | "重置" button clears all 8 filters and refetches | Click reset, verify cleared |
| AC-11 | Pagination preserves active filters | Filter, go to page 2, verify params |
| AC-12 | `stepFilter` coexists with server-side filters | Navigate from dashboard with step, add filter |
| AC-13 | Empty filter values NOT sent to API (clean URLs) | Check network: no `&client_id=&case_type=` |
| AC-14 | `npm run lint` passes | Run command |
| AC-15 | `npm run typecheck` passes | Run command |
| AC-16 | `npm run build` passes | Run command |

---

## 8. Risk / Issues Log

| # | Risk | Impact | Mitigation |
|---|------|--------|-----------|
| R-1 | Backend enum values differ from original spec (UM vs UTL, FlowDir values) | Incorrect filter values → 0 results | **Resolved**: Used actual backend enum values from `enums.py` |
| R-2 | `CaseFilterParams` defined in `cases.ts` instead of `cases.types.ts` | Minor code organization concern | Accept for now; follow-up cleanup can move to `.types.ts` |
| R-3 | Client dropdown loads max 100 clients | Large client base might be incomplete | Acceptable for MVP — matches CaseCreate.vue pattern (line 228) |
| R-4 | Agent ID is plain text input (UUID format) | UX not ideal — user must know UUID | No user list endpoint available; consistent with CaseCreate.vue (line 135) |
| R-5 | Legacy status values (PENDING, WITHDRAWN, ABANDONED, EXPIRED) not in CASE_STATUS_TEXT | Users can't filter by these statuses | Legacy values unlikely in active use; can add to displayText.ts if needed |
| R-6 | `reactive()` spread into function params | Must ensure reactivity unwraps correctly | `...filters` on a `reactive` object returns plain values — works correctly in Vue 3 |

---

## 9. Task Decomposition

| Task | File(s) | Description | Est. Lines Changed |
|------|---------|-------------|-------------------|
| **T1** | `cases.ts` | Add `CaseFilterParams` interface, update `getCases()` to pass filter params | ~20 lines |
| **T2** | `CaseList.vue` | Add filter panel template, filter state, client loading, search/reset handlers, styles | ~120 lines |
| **T3** | Quality gate | `npm run lint && npm run typecheck && npm run build` | 0 (validation only) |
| **T4** | Review | Read final code, verify all 16 acceptance criteria | 0 (review only) |

**Dependency graph**: T1 → T2 → T3 → T4 (strictly sequential — T2 depends on T1's getCases signature)

---

## 10. Implementation Notes for Agents

### For T1 Agent (cases.ts):
- Do NOT export `CaseFilterParams` — keep it file-private
- `CaseFilterParams extends CaseListParams` — import is already on line 3
- Use rest spread pattern: `const { page = 1, page_size = 20, ...filters } = params`
- Strip empty values with a simple loop before passing to `http.get`

### For T2 Agent (CaseList.vue):
- Use `reactive()` for `filters` object (consistent with CaseCreate.vue pattern)
- Import `getClients` from `'../../../api/clients'` and `Client` type from `'../../../api/clients.types'`
- Import `CASE_STATUS_TEXT` from `'../../../constants/displayText'`
- Status dropdown: iterate `CASE_STATUS_TEXT` record with `v-for="(label, key) in statusOptions"`
- Filter panel goes ABOVE the existing stepFilter subtitle div
- `fetchClientOptions()` called in `onMounted()` alongside existing `fetchCases()`
- Spread `...filters` into getCases params inside existing `fetchCases()` function
- Add `<style scoped>` rules for `.filter-panel` and `.filter-item`
