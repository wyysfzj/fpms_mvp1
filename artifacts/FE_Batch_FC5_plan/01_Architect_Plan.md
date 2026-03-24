# FC5 — Cross-entity List Enrichment: Detailed Execution Plan

## 1. Backend API Contract Summary (Confirmed)

### GET /api/v1/tasks
- **Enriched fields**: `case_no` (string|null), `client_name` (string|null) — batch-resolved via Case→Client join
- **Filter params**: `status`, `case_id`, `worker_id`, `supervisor_id`, `due_from`, `due_to`, `client_id` (NEW)
- Source: `backend/app/modules/tasks/api.py:98-179`

### GET /api/v1/documents
- **Enriched fields**: `case_no` (string|null) — batch-resolved via Case join
- **Filter params**: `q`, `direction`, `doc_template_id`, `case_id`, `client_id` (NEW), `date_from`, `date_to`
- Source: `backend/app/modules/documents/api.py:121-191`

---

## 2. Pre-existing Implementation Inventory

| File | What Already Exists | Status |
|------|-------------------|--------|
| `tasks.types.ts:10` | `case_no?: string` in Task | ✅ Done |
| `tasks.types.ts:41` | `case_id?: string` in TaskListParams | ✅ Done |
| `tasks.ts:9` | `case_no` in BackendTask | ✅ Done |
| `tasks.ts:30` | `case_no` mapped in mapTask() | ✅ Done |
| `tasks.ts:83-85` | `case_id` passed in getTasks() | ✅ Done |
| `documents.types.ts:10` | `case_no?: string` in Document | ✅ Done |
| `documents.ts:38` | `case_no` in BackendDocument | ✅ Done |
| `documents.ts:66` | `case_no` mapped in mapDocument() | ✅ Done |
| `TaskList.vue:56-63` | case_no column with router-link | ✅ Done |
| `DocumentList.vue:62-68` | case_no column with router-link | ✅ Done |

---

## 3. Changes Required Per File

### 3.1 `frontend/src/api/tasks.types.ts`

**Add `client_name` to Task interface (after line 10):**
```typescript
// Line 10: case_no?: string
client_name?: string    // NEW — from backend B6 enrichment
```

**Add `client_id` to TaskListParams (after line 41):**
```typescript
export interface TaskListParams {
    page?: number
    page_size?: number
    status?: string
    case_id?: string
    client_id?: string    // NEW — client_id filter
}
```

### 3.2 `frontend/src/api/documents.types.ts`

**Add `client_id` to DocumentListParams (after line 27):**
```typescript
export interface DocumentListParams {
    page?: number
    page_size?: number
    direction?: 'IN' | 'OUT'
    case_id?: string
    client_id?: string    // NEW — client_id filter
}
```

### 3.3 `frontend/src/api/tasks.ts`

**Add `client_name` to BackendTask interface (after line 9):**
```typescript
interface BackendTask {
    // ... existing fields ...
    case_no?: string | null
    client_name?: string | null    // NEW
    // ... rest of fields ...
}
```

**Add `client_name` mapping in mapTask() (after line 30):**
```typescript
function mapTask(input: BackendTask): Task {
    return {
        // ... existing fields ...
        case_no: input.case_no || undefined,
        client_name: input.client_name || undefined,    // NEW
        // ... rest of fields ...
    }
}
```

**Pass `client_id` in getTasks() (line 83):**
```typescript
export async function getTasks(params: TaskListParams = {}): Promise<Pagination<Task>> {
    const { page = 1, page_size = 20, status, case_id, client_id } = params    // ADD client_id
    const response = await http.get<Pagination<BackendTask>>('/tasks', {
        params: {
            page, page_size,
            ...(status ? { status } : {}),
            ...(case_id ? { case_id } : {}),
            ...(client_id ? { client_id } : {}),    // NEW
        }
    })
    // ...
}
```

### 3.4 `frontend/src/api/documents.ts`

**Pass `client_id` in getDocuments() (line 104-108):**
```typescript
export async function getDocuments(params: DocumentListParams = {}): Promise<Pagination<Document>> {
    const { page = 1, page_size = 20, direction, case_id, client_id } = params    // ADD client_id
    const response = await http.get<Pagination<BackendDocument>>('/documents', {
        params: {
            page, page_size,
            ...(direction ? { direction } : {}),
            ...(case_id ? { case_id } : {}),
            ...(client_id ? { client_id } : {}),    // NEW
        }
    })
    // ...
}
```

### 3.5 `frontend/src/modules/tasks/pages/TaskList.vue`

**Template changes — add client_id filter to filter bar:**
```html
<!-- Filter Bar — extend el-row -->
<el-row :gutter="16" style="margin-bottom: 16px">
  <el-col :span="6">
    <el-select v-model="filterStatus" placeholder="全部" clearable @change="onFilterChange">
      <el-option label="全部" value="" />
      <el-option label="待处理" value="OPEN" />
      <el-option label="已完成" value="DONE" />
      <el-option label="已取消" value="CANCELLED" />
    </el-select>
  </el-col>
  <!-- NEW: client filter -->
  <el-col :span="6">
    <el-select
      v-model="filterClientId"
      placeholder="全部客户"
      clearable
      filterable
      @change="onFilterChange"
    >
      <el-option
        v-for="c in clientOptions"
        :key="c.id"
        :label="c.name"
        :value="c.id"
      />
    </el-select>
  </el-col>
</el-row>
```

**Template changes — add client_name column (after case_no column, before status column):**
```html
<el-table-column label="客户" width="140">
  <template #default="{ row }">
    {{ row.client_name || '-' }}
  </template>
</el-table-column>
```

**Script changes:**
```typescript
// Add imports
import { getClients } from '../../../api/clients'
import type { Client } from '../../../api/clients.types'

// Add reactive state
const filterClientId = ref('')
const clientOptions = ref<Client[]>([])

// Modify fetchTasks to pass client_id
async function fetchTasks() {
  loading.value = true
  error.value = null
  try {
    const result = await getTasks({
      page: page.value,
      page_size: pageSize.value,
      status: filterStatus.value || undefined,
      client_id: filterClientId.value || undefined,    // NEW
    })
    tasks.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

// Load clients on mount
async function loadClients() {
  try {
    const result = await getClients({ page: 1, page_size: 9999 })
    clientOptions.value = result.items
  } catch {
    // silently ignore — filter just won't have options
  }
}

// Modify onMounted
onMounted(() => {
  fetchTasks()
  loadClients()
})
```

### 3.6 `frontend/src/modules/documents/pages/DocumentList.vue`

**Template changes — add client_id filter to filter bar:**
```html
<!-- Filter Bar — extend el-row -->
<el-row :gutter="16" style="margin-bottom: 16px">
  <el-col :span="6">
    <el-select v-model="filterDirection" placeholder="全部" clearable @change="onFilterChange">
      <el-option label="全部" value="" />
      <el-option label="收文" value="IN" />
      <el-option label="发文" value="OUT" />
    </el-select>
  </el-col>
  <!-- NEW: client filter -->
  <el-col :span="6">
    <el-select
      v-model="filterClientId"
      placeholder="全部客户"
      clearable
      filterable
      @change="onFilterChange"
    >
      <el-option
        v-for="c in clientOptions"
        :key="c.id"
        :label="c.name"
        :value="c.id"
      />
    </el-select>
  </el-col>
</el-row>
```

**Script changes:**
```typescript
// Add imports
import { getClients } from '../../../api/clients'
import type { Client } from '../../../api/clients.types'

// Add reactive state
const filterClientId = ref('')
const clientOptions = ref<Client[]>([])

// Modify fetchDocuments to pass client_id
async function fetchDocuments() {
  loading.value = true
  error.value = null
  try {
    const result = await getDocuments({
      page: page.value,
      page_size: pageSize.value,
      direction: filterDirection.value || undefined,
      client_id: filterClientId.value || undefined,    // NEW
    })
    documents.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

// Load clients on mount
async function loadClients() {
  try {
    const result = await getClients({ page: 1, page_size: 9999 })
    clientOptions.value = result.items
  } catch {
    // silently ignore — filter just won't have options
  }
}

// Modify onMounted
onMounted(() => {
  fetchDocuments()
  loadClients()
})
```

---

## 4. Chinese Label Mapping

| English key | 中文 label | Used in |
|-------------|-----------|---------|
| client (column) | 客户 | TaskList.vue column header |
| All clients (placeholder) | 全部客户 | TaskList.vue, DocumentList.vue filter placeholder |

Note: No new labels.zh.ts entries needed — "客户" is already defined in `ZH.taskList` and `ZH.docList` if needed, but for consistency with current code that uses inline Chinese strings in filters (see "全部", "待处理", "收文" etc.), we use inline strings for the new filter. The column header uses inline "客户" directly (consistent with BillList.vue pattern at line 58).

---

## 5. Component Design

### Client Filter (el-select)
- **Component**: `<el-select>` with `filterable` prop for type-ahead search
- **Data source**: `getClients({ page: 1, page_size: 9999 })` loaded on mount
- **Value binding**: `filterClientId` (string ref, empty = no filter)
- **Options**: `Client.id` as value, `Client.name` as label
- **Behavior**: clearable, triggers `onFilterChange()` → resets page to 1 and re-fetches
- **Pattern**: Same as existing status filter pattern in both pages

### Client Name Column (TaskList only)
- **Column**: `<el-table-column label="客户" width="140">` with fallback to `'-'`
- **Position**: After case_no column, before status column
- **DocumentList**: No client_name column added (backend documents endpoint doesn't return client_name)

---

## 6. Risk Areas

| Risk | Mitigation |
|------|-----------|
| Large client list (>1000) may slow filter | `filterable` prop on el-select enables type-ahead; page_size=9999 covers most PoC/MVP scenarios |
| Backend client_id filter not yet deployed | Verify backend has `client_id` query param — **CONFIRMED** in both api.py endpoints |
| `getClients` import path distance | 3 levels up: `../../../api/clients` — consistent with existing imports in both pages |
| client_name null when task has no case | Backend returns `null` for client_name when `case_id` is null — frontend shows `'-'` |

---

## 7. Quality Gate Checklist

After implementation, run:
```bash
cd frontend && npm run lint && npm run typecheck && npm run build
```

Expected: zero errors across all three gates.

---

## 8. Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| AC-1 | Task interface has `client_name?: string` | Read `tasks.types.ts` |
| AC-2 | TaskListParams has `client_id?: string` | Read `tasks.types.ts` |
| AC-3 | DocumentListParams has `client_id?: string` | Read `documents.types.ts` |
| AC-4 | BackendTask has `client_name` field | Read `tasks.ts` |
| AC-5 | mapTask() maps `client_name` | Read `tasks.ts` |
| AC-6 | getTasks() passes `client_id` param | Read `tasks.ts` |
| AC-7 | getDocuments() passes `client_id` param | Read `documents.ts` |
| AC-8 | TaskList.vue shows "客户" column with `client_name` | Read `TaskList.vue` |
| AC-9 | TaskList.vue has client_id el-select filter | Read `TaskList.vue` |
| AC-10 | DocumentList.vue has client_id el-select filter | Read `DocumentList.vue` |
| AC-11 | Both pages load client options on mount | Read both .vue files |
| AC-12 | `npm run lint` passes | CI gate |
| AC-13 | `npm run typecheck` passes | CI gate |
| AC-14 | `npm run build` passes | CI gate |

---

## 9. Task Dependency Graph

```
Task #2 (types) ──┐
                   ├──→ Task #4 (TaskList.vue)   ──┐
Task #3 (mappers) ─┘                                ├──→ Task #6 (QA) ──→ Task #7 (Review)
                   ┌──→ Task #5 (DocumentList.vue) ─┘
Task #2 (types) ──┘
Task #3 (mappers) ─┘
```

Tasks #2 and #3 can run in parallel or sequentially (no cross-dependency).
Tasks #4 and #5 depend on #2 and #3 being complete.
Task #6 depends on #4 and #5.
Task #7 depends on #6.

---

## 10. File Allowlist (Strict — No Other Files)

1. `frontend/src/api/tasks.types.ts`
2. `frontend/src/api/tasks.ts`
3. `frontend/src/api/documents.types.ts`
4. `frontend/src/api/documents.ts`
5. `frontend/src/modules/tasks/pages/TaskList.vue`
6. `frontend/src/modules/documents/pages/DocumentList.vue`
