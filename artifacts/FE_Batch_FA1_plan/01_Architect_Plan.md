# Batch FA1 — Case Detail Tab Completion — Architect Plan

> **Author**: Architect Agent
> **Date**: 2026-02-26
> **Status**: Ready for Implementation

---

## 1. Batch FA1 Summary

**Goal**: Replace 4 stubbed (placeholder) tabs in `CaseDetail.vue` with real data views, using existing backend API endpoints filtered by `case_id`.

**What changes**:
- 4 new Vue components (`CaseDocumentsTab`, `CaseTasksTab`, `CaseFeesTab`, `CaseClaimsTab`)
- `CaseDetail.vue` wires in new components, replacing `📄 待实现` placeholders
- 2 API client files updated to support `case_id` filtering
- 2 case API files updated to expose applicants/inventors data

**What doesn't change**:
- No backend changes required (all 3 API endpoints already support `case_id` filtering)
- No new routes, no new pages
- The "Overview" (tab 0) and "Billing" (tab 4) tabs remain untouched
- No inline editing — tabs are read-only views with navigation buttons

---

## 2. Backend Dependency Verification

All 3 backend endpoints **already support** `case_id` as a query parameter:

| Endpoint | Parameter | Verified In |
|----------|-----------|-------------|
| `GET /api/v1/documents` | `case_id: str \| None = Query(default=None)` | `backend/app/modules/documents/api.py:126` |
| `GET /api/v1/tasks` | `case_id: str \| None = Query(default=None)` | `backend/app/modules/tasks/api.py:105` |
| `GET /api/v1/fees/drafts` | `case_id: str \| None = Query(default=None)` | `backend/app/modules/fees/api.py:39` |

**Case detail** (`GET /api/v1/cases/{id}`) returns structured sub-tables:
- `applicants`: `[{seq, is_first, name_cn, name_en, address_cn, address_en}]`
- `inventors`: `[{seq, name_cn, name_en}]`

**Conclusion: FA1 requires NO backend changes.**

---

## 3. File Allowlist

### Extended Allowlist (11 files total)

The original spec lists 5 files. After thorough code analysis, **6 additional API client files** are needed to properly pass `case_id` and expose applicants/inventors data. This avoids technical debt and follows existing patterns.

| # | File | Action | Reason |
|---|------|--------|--------|
| 1 | `frontend/src/modules/cases/pages/CaseDetail.vue` | **MODIFY** | Wire in 4 tab components |
| 2 | `frontend/src/modules/cases/components/CaseDocumentsTab.vue` | **NEW** | Documents tab |
| 3 | `frontend/src/modules/cases/components/CaseTasksTab.vue` | **NEW** | Tasks tab |
| 4 | `frontend/src/modules/cases/components/CaseFeesTab.vue` | **NEW** | Fees tab |
| 5 | `frontend/src/modules/cases/components/CaseClaimsTab.vue` | **NEW** | Claims tab |
| 6 | `frontend/src/api/documents.ts` | **MODIFY** | Add `case_id` param to `getDocuments()` |
| 7 | `frontend/src/api/documents.types.ts` | **MODIFY** | Add `case_id` to `DocumentListParams` |
| 8 | `frontend/src/api/tasks.ts` | **MODIFY** | Add `case_id` param to `getTasks()` |
| 9 | `frontend/src/api/tasks.types.ts` | **MODIFY** | Add `case_id` to `TaskListParams` |
| 10 | `frontend/src/api/cases.ts` | **MODIFY** | Map applicants/inventors in `mapCase()` |
| 11 | `frontend/src/api/cases.types.ts` | **MODIFY** | Add `CaseApplicant`, `CaseInventor` types; update `Case` interface |

**Justification for extended allowlist**:
- Files 6-9: `getDocuments()` and `getTasks()` currently don't pass `case_id` to the backend. Without this fix, the tab components would need to either (a) fetch ALL records and filter client-side (wasteful, existing tech debt in `CaseRelatedTasks.vue`), or (b) use raw `http.get` calls bypassing the typed API layer (inconsistent pattern).
- Files 10-11: The `Case` type has `inventors?: string[]` but the backend returns `{seq, name_cn, name_en}` objects. `mapCase()` also completely drops both `applicants` and `inventors` from the response. Without this fix, the Claims tab would have no data.

---

## 4. Current State Analysis

### Tab Structure in CaseDetail.vue

`CaseDetail.vue:63-141` defines an `el-tabs` with 6 tabs:

| Tab Name | Label (ZH) | Current State |
|----------|------------|---------------|
| `overview` | 概览 | ✅ Implemented — shows case info grid |
| `claims` | 权利要求 | ❌ Placeholder — `📄 待实现` |
| `docs` | 官方文件 | ❌ Placeholder — `📁 待实现` |
| `fees` | 费用 | ❌ Placeholder — `💰 待实现` |
| `billing` | 账单 | ✅ Implemented — `CaseReceiptsSummary` component |
| `tasks` | 任务 | ❌ Placeholder — `✅ 待实现` |

### Existing Component Patterns

Components in `frontend/src/modules/cases/components/` follow these patterns:
- **Props**: `caseId: string` (or `status: string` for CaseStepper)
- **Data fetching**: `onMounted(async () => { ... })` with try/catch
- **Imports**: Relative paths `../../../api/xxx` and `../../../constants/labels.zh`
- **Loading state**: `const loading = ref(true)` initially true, set false in `finally`
- **Element Plus**: `el-table`, `el-tag`, `el-button`, `el-skeleton`
- **ZH labels**: All user-facing text from `ZH` constant

---

## 5. API Contract Documentation

### 5.1 Documents — `GET /api/v1/documents?case_id={id}`

**Frontend function**: `getDocuments({ case_id, page, page_size })` (after fix)

**Query params**: `page`, `page_size`, `case_id`, `direction`, `q`, `doc_template_id`, `client_id`, `date_from`, `date_to`

**Response** (`Pagination<BackendDocument>`):
```typescript
{
  items: [{
    id: string,
    case_id: string | null,
    case_no: string | null,      // batch-resolved by backend
    doc_template_id: string | null,
    direction: "IN" | "OUT",
    doc_date: string | null,
    title: string | null,
    ref_no: string | null,
    extra_data: string | null,
    reply_to_id: string | null,   // B2 field
    need_reply: boolean | null,   // B2 field
    reply_date: string | null,    // B2 field
    created_at: string,
    updated_at: string,
  }],
  page: number,
  page_size: number,
  total: number
}
```

**Frontend mapping**: `mapDocument()` in `documents.ts` maps `BackendDocument → Document`

### 5.2 Tasks — `GET /api/v1/tasks?case_id={id}`

**Frontend function**: `getTasks({ case_id, page, page_size })` (after fix)

**Query params**: `page`, `page_size`, `case_id`, `status`, `due_from`, `due_to`, `worker_id`, `supervisor_id`, `client_id`

**Response** (`Pagination<BackendTask>`):
```typescript
{
  items: [{
    id: string,
    case_id: string | null,
    case_no: string | null,      // batch-resolved
    client_name: string | null,  // batch-resolved
    document_id: string | null,
    task_template_id: string,
    title: string,
    due_date: string | null,
    internal_due_date: string | null,
    worker_id: string | null,
    supervisor_id: string | null,
    remark: string | null,
    status: string,
    created_at: string,
    updated_at: string,
  }],
  page: number,
  page_size: number,
  total: number
}
```

**Frontend mapping**: `mapTask()` in `tasks.ts` maps `BackendTask → Task`

### 5.3 Fee Drafts — `GET /api/v1/fees/drafts?case_id={id}`

**Frontend function**: `getFeeDrafts({ case_id, page, page_size })` (already works)

**Query params**: `page`, `page_size`, `case_id`, `client_id`, `status`

**Response** (`Pagination<FeeDraftListItem>`):
```typescript
{
  items: [{
    id: string,
    case_id: string,
    client_id: string | null,
    currency: string,
    status: "OPEN" | "LOCKED",
    amount: number | string,
  }],
  page: number,
  page_size: number,
  total: number
}
```

**Frontend mapping**: No mapping needed — `getFeeDrafts` returns raw response.

### 5.4 Case Detail — Applicants & Inventors

**Already loaded** in `CaseDetail.vue` via `getCase(id)`.

**Backend response** for `GET /api/v1/cases/{id}` includes:
```typescript
{
  // ... other fields ...
  applicants: [
    { seq: number, is_first: boolean, name_cn: string|null, name_en: string|null, address_cn: string|null, address_en: string|null }
  ],
  inventors: [
    { seq: number, name_cn: string|null, name_en: string|null }
  ],
}
```

**Current frontend issue**: `mapCase()` in `cases.ts` creates a new object that does NOT include `applicants` or `inventors`. The `BackendCase` interface also omits them. The `Case` type has `inventors?: string[]` which is the wrong shape.

---

## 6. Implementation Spec per Component

### 6.1 API Client Fixes (Pre-requisite)

#### `documents.types.ts` — Add `case_id` to `DocumentListParams`
```typescript
export interface DocumentListParams {
    page?: number
    page_size?: number
    direction?: 'IN' | 'OUT'
    case_id?: string          // ADD
}
```

#### `documents.ts` — Pass `case_id` in `getDocuments()`
```typescript
export async function getDocuments(params: DocumentListParams = {}): Promise<Pagination<Document>> {
    const { page = 1, page_size = 20, direction, case_id } = params   // ADD case_id
    const response = await http.get<Pagination<BackendDocument>>('/documents', {
        params: { page, page_size, ...(direction ? { direction } : {}), ...(case_id ? { case_id } : {}) }   // ADD case_id spread
    })
    // ... rest unchanged
}
```

#### `tasks.types.ts` — Add `case_id` to `TaskListParams`
```typescript
export interface TaskListParams {
    page?: number
    page_size?: number
    status?: string
    case_id?: string          // ADD
}
```

#### `tasks.ts` — Pass `case_id` in `getTasks()`
```typescript
export async function getTasks(params: TaskListParams = {}): Promise<Pagination<Task>> {
    const { page = 1, page_size = 20, status, case_id } = params   // ADD case_id
    const response = await http.get<Pagination<BackendTask>>('/tasks', {
        params: { page, page_size, ...(status ? { status } : {}), ...(case_id ? { case_id } : {}) }   // ADD case_id spread
    })
    // ... rest unchanged
}
```

#### `cases.types.ts` — Add applicant/inventor types, update Case
```typescript
// ADD new types
export interface CaseApplicant {
    seq: number
    is_first: boolean
    name_cn?: string
    name_en?: string
    address_cn?: string
    address_en?: string
}

export interface CaseInventor {
    seq: number
    name_cn?: string
    name_en?: string
}

// UPDATE Case interface
export interface Case {
    // ... existing fields ...
    applicants?: CaseApplicant[]   // ADD (replaces nothing)
    inventors?: CaseInventor[]     // CHANGE from string[] to CaseInventor[]
}
```

#### `cases.ts` — Update `BackendCase` and `mapCase()`
```typescript
// Add to BackendCase interface:
interface BackendCase {
    // ... existing fields ...
    applicants?: Array<{ seq: number; is_first: boolean; name_cn?: string; name_en?: string; address_cn?: string; address_en?: string }>
    inventors?: Array<{ seq: number; name_cn?: string; name_en?: string }>
}

// Update mapCase to include:
function mapCase(input: BackendCase): Case {
    return {
        // ... existing fields ...
        applicants: input.applicants || [],
        inventors: input.inventors || [],
    }
}
```

**Impact on existing code**: The `inventors` type change from `string[]` to `CaseInventor[]` affects `CaseDetail.vue` lines 150-161 where `{{ inventor }}` is used. After the fix, it should display `inventor.name_cn || inventor.name_en`. However, CaseDetail.vue is in our modify list, and the right-sidebar inventor display can be updated as part of the tab wiring changes.

---

### 6.2 CaseDocumentsTab.vue (NEW)

**Props**: `caseId: string`

**API call**: `getDocuments({ case_id: props.caseId, page: 1, page_size: 50 })`

**Template structure**:
```
<div>
  <div class="tab-header">
    <h3>官方文件</h3>
    <el-button size="small" type="primary" @click="navigateToCreate">
      登记文档
    </el-button>
  </div>

  <el-skeleton v-if="loading" :rows="5" animated />

  <el-table v-else-if="documents.length" :data="documents" stripe size="small">
    <el-table-column label="方向" width="80">
      <template #default="{ row }">
        <el-tag :type="row.direction === 'IN' ? 'success' : 'warning'" size="small">
          {{ row.direction === 'IN' ? '收文' : '发文' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="title" label="标题" />
    <el-table-column prop="doc_date" label="文档日期" width="120" />
    <el-table-column prop="created_at" label="创建时间" width="120" />
  </el-table>

  <div v-else class="empty-state">暂无官方文件</div>
</div>
```

**Actions**:
- "登记文档" button → `router.push('/documents/new?case_id=' + props.caseId)`

**State**: `documents: ref<Document[]>([])`, `loading: ref(true)`

---

### 6.3 CaseTasksTab.vue (NEW)

**Props**: `caseId: string`

**API call**: `getTasks({ case_id: props.caseId, page: 1, page_size: 50 })`

**Template structure**:
```
<div>
  <div class="tab-header">
    <h3>任务列表</h3>
    <el-button size="small" type="primary" @click="navigateToCreate">
      新建任务
    </el-button>
  </div>

  <el-skeleton v-if="loading" :rows="5" animated />

  <el-table v-else-if="tasks.length" :data="tasks" stripe size="small">
    <el-table-column prop="title" label="标题" />
    <el-table-column label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="taskStatusType(row.status)" size="small">
          {{ row.status }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="due_date" label="截止日期" width="120" />
    <el-table-column prop="assigned_to" label="负责人" width="120" />
    <el-table-column label="操作" width="160">
      <template #default="{ row }">
        <el-button v-if="row.status === 'OPEN'" size="small" @click="handleClose(row)">关闭</el-button>
        <el-button v-if="row.status === 'DONE'" size="small" @click="handleReopen(row)">重新打开</el-button>
      </template>
    </el-table-column>
  </el-table>

  <div v-else class="empty-state">暂无任务</div>
</div>
```

**Actions**:
- "新建任务" button → `router.push('/tasks/new?case_id=' + props.caseId)`
- "关闭" → `closeTask(task.id)` then refresh
- "重新打开" → `reopenTask(task.id)` then refresh

**Status tag mapping**:
```typescript
function taskStatusType(status: string) {
  switch (status) {
    case 'OPEN': return ''           // default (blue)
    case 'DONE': return 'success'
    case 'CANCELLED': return 'info'
    default: return 'info'
  }
}
```

**State**: `tasks: ref<Task[]>([])`, `loading: ref(true)`

---

### 6.4 CaseFeesTab.vue (NEW)

**Props**: `caseId: string`

**API call**: `getFeeDrafts({ case_id: props.caseId, page: 1, page_size: 50 })`

**Template structure**:
```
<div>
  <div class="tab-header">
    <h3>费用草稿</h3>
    <el-button size="small" type="primary" @click="navigateToCreate">
      新建草稿
    </el-button>
  </div>

  <el-skeleton v-if="loading" :rows="5" animated />

  <el-table v-else-if="drafts.length" :data="drafts" stripe size="small" @row-click="handleRowClick">
    <el-table-column label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="row.status === 'LOCKED' ? 'danger' : 'success'" size="small">
          {{ row.status === 'LOCKED' ? '已锁定' : '开放' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="currency" label="币种" width="80" />
    <el-table-column label="金额" width="130" align="right">
      <template #default="{ row }">
        <span class="mono-num">{{ formatAmount(row.amount, row.currency) }}</span>
      </template>
    </el-table-column>
  </el-table>

  <div v-else class="empty-state">暂无费用草稿</div>
</div>
```

**Actions**:
- "新建草稿" → `router.push('/fees/drafts/new?case_id=' + props.caseId)`
- Row click → `router.push('/fees/drafts/' + row.id)`

**State**: `drafts: ref<FeeDraftListItem[]>([])`, `loading: ref(true)`

---

### 6.5 CaseClaimsTab.vue (NEW)

**Props**: `applicants: CaseApplicant[]`, `inventors: CaseInventor[]`

**NO API call** — data is passed from parent (already loaded in CaseDetail.vue)

**Template structure**:
```
<div>
  <!-- Applicants Section -->
  <div class="claims-section">
    <h3>申请人</h3>
    <el-table v-if="applicants.length" :data="applicants" stripe size="small">
      <el-table-column prop="seq" label="序号" width="70" />
      <el-table-column prop="name_cn" label="中文名" />
      <el-table-column prop="name_en" label="英文名" />
      <el-table-column label="第一申请人" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.is_first" type="success" size="small">是</el-tag>
        </template>
      </el-table-column>
    </el-table>
    <div v-else class="empty-state">暂无申请人信息</div>
  </div>

  <!-- Inventors Section -->
  <div class="claims-section" style="margin-top: 24px;">
    <h3>发明人</h3>
    <el-table v-if="inventors.length" :data="inventors" stripe size="small">
      <el-table-column prop="seq" label="序号" width="70" />
      <el-table-column prop="name_cn" label="中文名" />
      <el-table-column prop="name_en" label="英文名" />
    </el-table>
    <div v-else class="empty-state">暂无发明人信息</div>
  </div>

  <div class="claims-note">
    <p>编辑申请人/发明人信息请前往案件编辑页面。</p>
  </div>
</div>
```

**No actions** — read-only display. Editing is done via the case edit page.

---

## 7. CaseDetail.vue Modification Plan

### 7.1 Imports to Add
```typescript
import CaseDocumentsTab from '../components/CaseDocumentsTab.vue'
import CaseTasksTab from '../components/CaseTasksTab.vue'
import CaseFeesTab from '../components/CaseFeesTab.vue'
import CaseClaimsTab from '../components/CaseClaimsTab.vue'
```

### 7.2 Tab Content Replacement

**Claims tab** (lines 100-107) — Replace placeholder with:
```html
<el-tab-pane :label="ZH.caseDetail.claims" name="claims">
  <div class="case-panel">
    <CaseClaimsTab
      :applicants="caseData.applicants || []"
      :inventors="caseData.inventors || []"
    />
  </div>
</el-tab-pane>
```

**Official Docs tab** (lines 109-116) — Replace placeholder with:
```html
<el-tab-pane :label="ZH.caseDetail.officialDocs" name="docs">
  <div class="case-panel">
    <CaseDocumentsTab :case-id="caseData.id" />
  </div>
</el-tab-pane>
```

**Fees tab** (lines 118-125) — Replace placeholder with:
```html
<el-tab-pane :label="ZH.caseDetail.fees" name="fees">
  <div class="case-panel">
    <CaseFeesTab :case-id="caseData.id" />
  </div>
</el-tab-pane>
```

**Tasks tab** (lines 133-140) — Replace placeholder with:
```html
<el-tab-pane :label="ZH.caseDetail.tasks" name="tasks">
  <div class="case-panel">
    <CaseTasksTab :case-id="caseData.id" />
  </div>
</el-tab-pane>
```

### 7.3 Right Sidebar Inventor Display Fix

Lines 149-161 currently display `{{ inventor }}` as a string. After the `Case.inventors` type change to `CaseInventor[]`, update to:
```html
<span v-for="(inventor, idx) in caseData.inventors" :key="idx" class="inventor-tag">
  {{ inventor.name_cn || inventor.name_en || '—' }}
</span>
```

---

## 8. Pattern Compliance

All new components follow patterns from existing case components:

| Pattern | Source Component | Applied In |
|---------|-----------------|------------|
| Props: `caseId: string` | `CaseRelatedTasks.vue:25-27` | Docs, Tasks, Fees tabs |
| Data fetch in `onMounted` | `CaseRelatedTasks.vue:32-41` | Docs, Tasks, Fees tabs |
| Loading skeleton | `CaseReceiptsSummary.vue:9-11` | Docs, Tasks, Fees tabs |
| `el-table` with `stripe size="small"` | `CaseReceiptsSummary.vue:36-72` | All 4 tabs |
| `el-tag` for status | `CaseReceiptsSummary.vue:49-53` | Docs direction, Tasks status, Fees status |
| Relative imports `../../../api/xxx` | All existing components | All 4 tabs |
| ZH labels from `../../../constants/labels.zh` | All existing components | All 4 tabs |
| Try/catch with silent fail for side panels | `CaseRelatedTasks.vue:36` | Could use, but tab components should show errors |

**Difference from side panel components**: Tab components should use proper error handling (show `ApiErrorBanner`) rather than silently failing, since they are the main content area not auxiliary panels.

---

## 9. Chinese Text Inventory

### New labels NOT in ZH constant (must use inline strings)

| Component | Text | Context |
|-----------|------|---------|
| CaseDocumentsTab | `登记文档` | Create button |
| CaseDocumentsTab | `暂无官方文件` | Empty state |
| CaseDocumentsTab | `收文` / `发文` | Direction badge |
| CaseDocumentsTab | `方向` / `标题` / `文档日期` / `创建时间` | Column headers |
| CaseTasksTab | `暂无任务` | Empty state (could reuse `ZH.relatedTasks.noTasks`) |
| CaseTasksTab | `标题` / `状态` / `截止日期` / `负责人` / `操作` | Column headers |
| CaseTasksTab | `关闭` / `重新打开` | Action buttons (could reuse `ZH.taskList.close` / `ZH.taskList.reopen`) |
| CaseFeesTab | `暂无费用草稿` | Empty state |
| CaseFeesTab | `状态` / `币种` / `金额` | Column headers |
| CaseFeesTab | `已锁定` / `开放` | Status labels |
| CaseClaimsTab | `申请人` / `发明人` | Section headers |
| CaseClaimsTab | `暂无申请人信息` / `暂无发明人信息` | Empty states |
| CaseClaimsTab | `序号` / `中文名` / `英文名` / `第一申请人` | Column headers |
| CaseClaimsTab | `编辑申请人/发明人信息请前往案件编辑页面。` | Note text |

**Strategy**: Use inline Chinese strings for tab-specific labels. Reuse `ZH.taskList.close`, `ZH.taskList.reopen`, `ZH.caseDetail.*` where they already exist. A comprehensive ZH table expansion is out of FA1 scope.

---

## 10. Risk Assessment

### Medium Risk
1. **`inventors` type change**: Changing `Case.inventors` from `string[]` to `CaseInventor[]` may break TypeScript compilation if any other component references `caseData.inventors` as strings. **Mitigation**: Search for all usages of `Case.inventors` before implementing. Only `CaseDetail.vue` lines 150-161 uses it, and that's in our modify list.

2. **`DocumentListParams.case_id` addition**: Existing callers of `getDocuments()` don't pass `case_id`, so no breakage. The param is optional.

### Low Risk
3. **Empty data**: If a case has no documents/tasks/fees, tabs show empty states. This is correct behavior.

4. **Task status action buttons**: `closeTask` and `reopenTask` send `POST` with `{}` body, but backend expects `TaskActionIn` which has optional `remark`. Existing `closeTask`/`reopenTask` functions in `tasks.ts` already send `{}` — this works because `remark` is optional.

5. **Navigation with query params**: Routes like `/documents/new?case_id=X` must be handled by the target create pages. If `DocumentCreate.vue` doesn't read `case_id` from query, the pre-fill won't work. This is **outside FA1 scope** but worth noting as a future enhancement.

### No Risk
6. **Fee drafts `getFeeDrafts`**: Already supports `case_id`. No changes needed to the fee API client.

---

## 11. Implementation Order

The recommended order for the frontend-agent:

1. **API client fixes first** (files 6-11) — prerequisite for everything else
   - `cases.types.ts` → add `CaseApplicant`, `CaseInventor`, update `Case`
   - `cases.ts` → update `BackendCase`, `mapCase`
   - `documents.types.ts` → add `case_id` to `DocumentListParams`
   - `documents.ts` → pass `case_id` in `getDocuments`
   - `tasks.types.ts` → add `case_id` to `TaskListParams`
   - `tasks.ts` → pass `case_id` in `getTasks`

2. **New components** (files 2-5) — can be created in any order
   - `CaseClaimsTab.vue` (simplest, no API call)
   - `CaseFeesTab.vue` (API client already ready)
   - `CaseDocumentsTab.vue`
   - `CaseTasksTab.vue` (most complex — has action buttons)

3. **CaseDetail.vue modification** (file 1) — last, wires everything together
   - Add imports
   - Replace 4 tab placeholders
   - Fix inventor display in sidebar

4. **Quality gate**: `cd frontend && npm run lint && npm run typecheck && npm run build`

---

## 12. Acceptance Criteria Checklist

- [ ] All 4 tabs show real data (not placeholder text "待实现")
- [ ] Docs tab shows documents linked to this case via `case_id` filter
- [ ] Tasks tab shows tasks linked to this case with status tags (OPEN/DONE/CANCELLED)
- [ ] Fees tab shows fee drafts linked to this case with amount and status
- [ ] Claims tab shows applicants table (seq, name_cn, name_en, is_first) and inventors table (seq, name_cn, name_en)
- [ ] "Create" buttons navigate to correct forms with `case_id` query param
- [ ] Task status action buttons (Close/Reopen) work and refresh the list
- [ ] Empty states shown when no data exists
- [ ] Right sidebar inventor display still works with new `CaseInventor` type
- [ ] Quality gate passes: `npm run lint && npm run typecheck && npm run build`
