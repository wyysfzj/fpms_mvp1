# FB4 Architect Plan — TaskTemplate Admin Page

## 1. Dependency Verification

### Backend A1 Task-Template APIs — CONFIRMED

| Endpoint | Method | Request Schema | Response | Permission |
|----------|--------|---------------|----------|------------|
| `/api/v1/task-templates` | GET | `?enabled_only=bool` | `TaskTemplateOut[]` | `TaskTemplate.Read` |
| `/api/v1/task-templates` | POST | `TaskTemplateCreateIn` | `TaskTemplateOut` (201) | `TaskTemplate.Create` |
| `/api/v1/task-templates/{template_id}` | PUT | `TaskTemplateUpdateIn` | `TaskTemplateOut` | `TaskTemplate.Edit` |

Verified in `backend/app/modules/tasks/api.py` lines 53-90 and `backend/app/modules/tasks/schemas.py` lines 103-136.

**Note**: GET returns a flat array (`list[TaskTemplateOut]`), NOT paginated. No pagination needed on frontend.

### Backend Schema — Exact Fields

```typescript
// TaskTemplateOut (GET/POST/PUT response)
{
  id: string           // UUID
  code: string         // unique identifier code
  name: string
  add_days: number | null
  add_months: number | null
  inner_offset_days: number | null
  default_worker_role: string | null
  enabled: boolean
  description: string | null
  created_at: string   // ISO datetime
  updated_at: string   // ISO datetime
}

// TaskTemplateCreateIn (POST body)
{
  code: string         // required, 1-64 chars
  name: string         // required, 1-256 chars
  add_days?: number | null
  add_months?: number | null
  inner_offset_days?: number | null
  default_worker_role?: string | null
  description?: string | null
}

// TaskTemplateUpdateIn (PUT body) — NO code field
{
  name?: string | null          // 1-256 chars
  add_days?: number | null
  add_months?: number | null
  inner_offset_days?: number | null
  default_worker_role?: string | null
  enabled?: boolean | null
  description?: string | null
}
```

---

## 2. File-by-File Change Specification

### File 1: `frontend/src/api/tasks.types.ts` (MODIFY)

**Action**: Append 3 new interfaces after existing types.

```typescript
// --- ADD after line 51 (end of TaskCreatePayload) ---

export interface TaskTemplate {
    id: string
    code: string
    name: string
    add_days: number | null
    add_months: number | null
    inner_offset_days: number | null
    default_worker_role: string | null
    enabled: boolean
    description: string | null
    created_at: string
    updated_at: string
}

export interface TaskTemplateCreatePayload {
    code: string
    name: string
    add_days?: number | null
    add_months?: number | null
    inner_offset_days?: number | null
    default_worker_role?: string | null
    description?: string | null
}

export interface TaskTemplateUpdatePayload {
    name?: string | null
    add_days?: number | null
    add_months?: number | null
    inner_offset_days?: number | null
    default_worker_role?: string | null
    enabled?: boolean | null
    description?: string | null
}
```

---

### File 2: `frontend/src/api/tasks.ts` (MODIFY)

**Action**: Add 3 new exported functions at end of file. Import new types.

**Import change** (line 3):
```typescript
// BEFORE
import type { Task, TaskCreatePayload, TaskListParams, TaskLog } from './tasks.types'

// AFTER
import type { Task, TaskCreatePayload, TaskListParams, TaskLog, TaskTemplate, TaskTemplateCreatePayload, TaskTemplateUpdatePayload } from './tasks.types'
```

**New functions** (append after `getTodayReminders`):

```typescript
// ── Task Template CRUD ─────────────────────────────────────

/**
 * List all task templates
 */
export async function getTaskTemplates(enabledOnly?: boolean): Promise<TaskTemplate[]> {
    const response = await http.get<TaskTemplate[]>('/task-templates', {
        params: enabledOnly != null ? { enabled_only: enabledOnly } : undefined,
    })
    return response.data
}

/**
 * Create a task template
 */
export async function createTaskTemplate(data: TaskTemplateCreatePayload): Promise<TaskTemplate> {
    const response = await http.post<TaskTemplate>('/task-templates', data)
    return response.data
}

/**
 * Update a task template
 */
export async function updateTaskTemplate(id: string, data: TaskTemplateUpdatePayload): Promise<TaskTemplate> {
    const response = await http.put<TaskTemplate>(`/task-templates/${id}`, data)
    return response.data
}
```

**Notes**:
- No `BackendX → FrontendX` mapping needed — schema is 1:1 with backend `TaskTemplateOut`.
- No pagination — backend returns flat array.

---

### File 3: `frontend/src/modules/system/pages/TaskTemplateList.vue` (NEW)

**Pattern reference**: `LetterheadList.vue` (dialog CRUD) + `TemplateList.vue` (table layout).

#### Template Structure

```
<div class="page-container">
  <!-- Page Header: title + count + "新增模板" button -->
  <!-- Error Banner -->
  <!-- LoadingBlock -->
  <!-- EmptyState -->
  <!-- el-table -->
    columns: code, name, add_days, add_months, inner_offset_days, default_worker_role, enabled (el-tag), actions
    actions: "编辑" button, "启用/停用" button
  <!-- Create/Edit Dialog -->
    form fields: code, name, add_days, add_months, inner_offset_days, default_worker_role, description, enabled
</div>
```

#### Script Setup — State Variables

```typescript
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules, InputInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getTaskTemplates, createTaskTemplate, updateTaskTemplate } from '../../../api/tasks'
import type { TaskTemplate, TaskTemplateCreatePayload, TaskTemplateUpdatePayload } from '../../../api/tasks.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'

// List state
const templates = ref<TaskTemplate[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const isEmpty = computed(() => !loading.value && !error.value && templates.value.length === 0)

// Dialog state (shared for create & edit)
const showDialog = ref(false)
const isEdit = ref(false)
const editingId = ref<string | null>(null)
const saving = ref(false)
const dialogError = ref<ApiError | null>(null)
const formRef = ref<FormInstance>()
const codeInputRef = ref<InputInstance>()
const fieldErrors = ref<Map<string, string[]>>(new Map())
const lastFocusedElement = ref<HTMLElement | null>(null)

const form = reactive({
    code: '',
    name: '',
    add_days: null as number | null,
    add_months: null as number | null,
    inner_offset_days: null as number | null,
    default_worker_role: '',
    description: '',
    enabled: true,
})

const formRules: FormRules = {
    code: [{ required: true, message: '编码为必填项', trigger: 'blur' }],
    name: [{ required: true, message: '名称为必填项', trigger: 'blur' }],
}
```

#### Key Functions

| Function | Purpose |
|----------|---------|
| `fetchTemplates()` | `getTaskTemplates()` → sets `templates` |
| `openCreateDialog()` | Reset form, `isEdit=false`, show dialog |
| `openEditDialog(row)` | Populate form from row, `isEdit=true`, `editingId=row.id`, show dialog |
| `handleDialogOpen()` | Focus first input on nextTick |
| `resetForm()` | Clear all form fields, errors |
| `restoreTriggerFocus()` | Restore focus after dialog close |
| `handleSave()` | Validate → if isEdit: `updateTaskTemplate(editingId, payload)` else `createTaskTemplate(payload)` → success msg → close → refetch |
| `handleToggleEnabled(row)` | `updateTaskTemplate(row.id, { enabled: !row.enabled })` → success msg → refetch |
| `formatDate(dateStr)` | Standard date formatting (same as other system pages) |

#### Table Columns

| Column | prop | width | Renderer |
|--------|------|-------|----------|
| 编码 | `code` | 150 | `<span class="template-code">` |
| 名称 | `name` | min-width 180 | plain text |
| 加天数 | `add_days` | 100 | `row.add_days ?? '—'` |
| 加月数 | `add_months` | 100 | `row.add_months ?? '—'` |
| 内部偏移天数 | `inner_offset_days` | 120 | `row.inner_offset_days ?? '—'` |
| 默认角色 | `default_worker_role` | 120 | `row.default_worker_role \|\| '—'` |
| 状态 | `enabled` | 80 | `<el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '停用' }}</el-tag>` |
| 操作 | — | 150 | "编辑" + "启用/停用" buttons |

#### Dialog Form Fields

| Field | Component | Props | Notes |
|-------|-----------|-------|-------|
| 编码 (code) | `el-input` | `:disabled="isEdit"`, `v-model.trim` | Read-only in edit mode |
| 名称 (name) | `el-input` | `v-model.trim` | Required |
| 加天数 (add_days) | `el-input-number` | `:min="0"`, `v-model` | Allow null |
| 加月数 (add_months) | `el-input-number` | `:min="0"`, `v-model` | Allow null |
| 内部偏移天数 (inner_offset_days) | `el-input-number` | `:min="0"`, `v-model` | Allow null |
| 默认角色 (default_worker_role) | `el-input` | `v-model.trim` | Optional |
| 描述 (description) | `el-input` | `type="textarea"`, `:rows="2"` | Optional |
| 启用 (enabled) | `el-switch` | `v-model` | Only shown in edit mode |

#### Scoped CSS

```css
.template-code { font-family: var(--font-mono); font-weight: 500; }
.dialog-error { margin-bottom: 16px; }
```

---

### File 4: `frontend/src/router/index.ts` (MODIFY)

**Action**: Add route after `system/letterheads` (line 199), before Focus Mode Demo.

```typescript
{
    path: 'system/task-templates',
    name: 'system_task_templates',
    component: () => import('../modules/system/pages/TaskTemplateList.vue'),
    meta: { requiredPerms: [Perms.SETTINGS_READ] }
},
```

**Insert position**: After the `system/letterheads` route block (line 199), before the `focus-demo` route (line 201).

---

### File 5: `frontend/src/constants/menu.ts` (MODIFY)

**Action**: Add menu item to `settings` group children array.

```typescript
// BEFORE (line 57-59):
children: [
    { key: 'settings', label: '系统配置', icon: '⚙️', route: '/system/params', requiredPerms: [Perms.SETTINGS_READ] },
],

// AFTER:
children: [
    { key: 'settings', label: '系统配置', icon: '⚙️', route: '/system/params', requiredPerms: [Perms.SETTINGS_READ] },
    { key: 'task_templates', label: '任务模板', icon: '📋', route: '/system/task-templates', requiredPerms: [Perms.SETTINGS_READ] },
],
```

---

## 3. API Contract Table

| Frontend Function | HTTP | Backend Endpoint | Request | Response | Used In |
|---|---|---|---|---|---|
| `getTaskTemplates(enabledOnly?)` | GET | `/api/v1/task-templates?enabled_only=` | query param | `TaskTemplate[]` | TaskTemplateList.vue `fetchTemplates()` |
| `createTaskTemplate(data)` | POST | `/api/v1/task-templates` | `TaskTemplateCreatePayload` JSON | `TaskTemplate` | TaskTemplateList.vue `handleSave()` |
| `updateTaskTemplate(id, data)` | PUT | `/api/v1/task-templates/{id}` | `TaskTemplateUpdatePayload` JSON | `TaskTemplate` | TaskTemplateList.vue `handleSave()`, `handleToggleEnabled()` |

---

## 4. Acceptance Criteria Checklist

- [ ] **AC-1**: `tasks.types.ts` exports `TaskTemplate`, `TaskTemplateCreatePayload`, `TaskTemplateUpdatePayload` interfaces matching backend schema exactly
- [ ] **AC-2**: `tasks.ts` exports `getTaskTemplates`, `createTaskTemplate`, `updateTaskTemplate` with correct HTTP methods and paths
- [ ] **AC-3**: `TaskTemplateList.vue` renders table with all 7 data columns + actions column
- [ ] **AC-4**: Create dialog opens, validates required fields (code, name), submits POST, shows success message, refreshes list
- [ ] **AC-5**: Edit dialog opens with pre-filled data, code field is disabled, submits PUT, shows success message, refreshes list
- [ ] **AC-6**: Toggle enabled/disabled via action button calls PUT with `{ enabled: !current }`, refreshes list
- [ ] **AC-7**: `enabled` column renders `<el-tag type="success">启用</el-tag>` or `<el-tag type="info">停用</el-tag>`
- [ ] **AC-8**: Route `/system/task-templates` loads TaskTemplateList.vue, requires `SETTINGS_READ` permission
- [ ] **AC-9**: Menu item "任务模板" appears under "系统设置" group with icon 📋 and route `/system/task-templates`
- [ ] **AC-10**: All imports use relative paths (no `@/` alias)
- [ ] **AC-11**: All user-facing text is in Chinese
- [ ] **AC-12**: Error handling follows project pattern (ApiErrorBanner, mapFieldErrors for 422)
- [ ] **AC-13**: Loading/empty/error states handled consistently with existing system pages
- [ ] **AC-14**: `npm run lint` passes
- [ ] **AC-15**: `npm run typecheck` passes
- [ ] **AC-16**: `npm run build` succeeds

---

## 5. Risk / Issues Log

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R1 | Backend permissions `TaskTemplate.Read/Create/Edit` may not be in seed data for admin role | Low | Admin has wildcard perms. If 403 returned, backend seed needs updating (out of FB4 scope). |
| R2 | `el-input-number` with `null` initial value may need `:controls="false"` or placeholder handling | Low | Use `v-model` directly; Element Plus handles null as empty. Set `placeholder="—"` and `:controls="true"`. |
| R3 | No DELETE endpoint exists for task templates | Info | By design — templates are disabled, not deleted. UI has no delete button. |
| R4 | `enabled` field not in `TaskTemplateCreateIn` schema | Info | New templates default to `enabled=true` on backend. Show `enabled` switch only in edit dialog. |

---

## 6. Task Decomposition & Assignment

| Task ID | Subject | Files | Depends On | Est. Lines |
|---------|---------|-------|------------|------------|
| T1 | Add TaskTemplate types to `tasks.types.ts` | tasks.types.ts | — | ~35 |
| T2 | Add TaskTemplate CRUD API functions to `tasks.ts` | tasks.ts | T1 | ~30 |
| T3 | Create `TaskTemplateList.vue` page | TaskTemplateList.vue (new) | T1, T2 | ~300 |
| T4 | Add `/system/task-templates` route | router/index.ts | T3 | ~5 |
| T5 | Add 任务模板 menu item | constants/menu.ts | — | ~2 |

**Parallelism**: T1+T5 can run in parallel. T2 depends on T1. T3 depends on T1+T2. T4 depends on T3.

**Recommended assignment**: Single impl agent handles T1→T2→T3→T4→T5 sequentially (small batch, tight dependencies).
