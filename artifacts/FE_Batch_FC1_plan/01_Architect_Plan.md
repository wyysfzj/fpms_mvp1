# FC1 — DocTemplate Admin UI: Architect Execution Plan

**Author**: Architect Agent
**Date**: 2026-02-27
**Batch**: FC1
**Status**: VERIFIED — ready for implementation

---

## 1. Scope Summary

Create a **DocTemplate management page** under System Settings that allows admins to list, create, and edit document templates. These templates drive the configuration-driven document automation system built by backend B1.

**Deliverables**: 5 files (3 modify, 1 new, 1 modify menu)

---

## 2. Backend Dependency Verification

### 2.1 Backend B1 Endpoints — CONFIRMED

All 4 endpoints exist in `backend/app/modules/documents/api.py` (lines 51–113), registered under the **Documents** router (no prefix — routes are `/doc-templates`):

| Method | Path | Permission | Response | Status |
|--------|------|-----------|----------|--------|
| GET | `/api/v1/doc-templates` | `DocTemplate.Read` | `DocTemplateListOut` (paginated) | **CONFIRMED** (line 51) |
| POST | `/api/v1/doc-templates` | `DocTemplate.Create` | `DocTemplateOut` (201) | **CONFIRMED** (line 72) |
| GET | `/api/v1/doc-templates/{template_id}` | `DocTemplate.Read` | `DocTemplateOut` | **CONFIRMED** (line 87) |
| PUT | `/api/v1/doc-templates/{template_id}` | `DocTemplate.Edit` | `DocTemplateOut` | **CONFIRMED** (line 101) |

**Query params for GET list**: `q` (text search), `direction` (IN/OUT enum), `enabled` (bool), `page`, `page_size`

### 2.2 DocTemplate Model — CONFIRMED

From `backend/app/modules/documents/models.py` (line 30–48), model `DocTemplate` (`t_doc_template`):

| Field | Type | Nullable | Default | Notes |
|-------|------|----------|---------|-------|
| id | UUID (String 36) | NO | auto | from UUIDPrimaryKeyMixin |
| code | String(64) | NO | — | unique=True |
| name | String(256) | NO | — | — |
| direction | String(8) | NO | `'IN'` | server_default |
| enabled | Boolean | NO | `1` (true) | server_default |
| status_effect | String(32) | YES | null | — |
| status_restore | String(32) | YES | null | — |
| deadline_template_code | String(64) | YES | null | references TaskTemplate.code |
| fee_draft_type | String(32) | YES | null | — |
| fee_item_list | Text | YES | null | JSON string |
| need_reply | Boolean | YES | `0` (false) | server_default |
| reply_to_template_code | String(64) | YES | null | — |
| input_fields | Text | YES | null | JSON string |
| created_at | DateTime | auto | auto | from AuditMixin |
| updated_at | DateTime | auto | auto | from AuditMixin |

### 2.3 Backend Schemas — CONFIRMED

From `backend/app/modules/documents/schemas.py` (lines 69–119):

- `DocTemplateCreateIn`: code (required), name (required), direction (default IN), enabled (default true), + optional spec fields
- `DocTemplateUpdateIn`: all fields optional except code (not updatable)
- `DocTemplateOut`: all fields including created_at, updated_at. Uses `ConfigDict(from_attributes=True)`
- `DocTemplateListOut`: extends `PageResult[DocTemplateOut]` → `{ items, page, page_size, total }`

### 2.4 DocumentDirection Enum — CONFIRMED

From `backend/app/modules/documents/enums.py`: `IN` | `OUT` (string enum)

### 2.5 TaskTemplate List Endpoint (for deadline_template_code dropdown)

From `backend/app/modules/tasks/api.py` via `frontend/src/api/tasks.ts` line 142:
- `GET /api/v1/task-templates` → returns `TaskTemplate[]` (array, not paginated)
- Can pass `enabled_only` query param
- Frontend function: `getTaskTemplates(enabledOnly?: boolean)`
- TaskTemplate has `code` and `name` fields — we need `code` for dropdown value, `name` for display

### 2.6 Router Registration

From `backend/app/api/router.py` line 23: `documents_router` is included without prefix, so routes are at `/api/v1/doc-templates` (the `/api/v1` prefix comes from `main.py`).

---

## 3. Verified Field Mappings

Backend `DocTemplateOut` fields map 1:1 to frontend types. No mapping layer needed (unlike Document which has field renaming). Backend field names will be used directly.

| Backend Field | Frontend Type | Form Control | Table Column |
|--------------|---------------|-------------|--------------|
| id | string | — | — |
| code | string | el-input (required, disabled on edit) | YES |
| name | string | el-input (required) | YES |
| direction | `'IN' \| 'OUT'` | el-select | YES |
| enabled | boolean | el-switch | YES (tag) |
| status_effect | string \| null | el-input | YES |
| status_restore | string \| null | el-input | NO (dialog only) |
| deadline_template_code | string \| null | el-select (from TaskTemplates) | YES |
| fee_draft_type | string \| null | el-input | YES |
| fee_item_list | string \| null | el-input type="textarea" (JSON) | NO (dialog only) |
| need_reply | boolean \| null | el-switch | YES |
| reply_to_template_code | string \| null | el-input | NO (dialog only) |
| input_fields | string \| null | el-input type="textarea" (JSON) | NO (dialog only) |
| created_at | string (datetime) | — | NO |
| updated_at | string (datetime) | — | NO |

---

## 4. File-by-File Change Spec

### File 1: `frontend/src/api/documents.types.ts` (MODIFY)

**Action**: Append DocTemplate type interfaces at the end of the file.

**Add these types**:

```typescript
// DocTemplate types (FC1)

export interface DocTemplate {
    id: string
    code: string
    name: string
    direction: 'IN' | 'OUT'
    enabled: boolean
    status_effect: string | null
    status_restore: string | null
    deadline_template_code: string | null
    fee_draft_type: string | null
    fee_item_list: string | null
    need_reply: boolean | null
    reply_to_template_code: string | null
    input_fields: string | null
    created_at: string
    updated_at: string
}

export interface DocTemplateListParams {
    page?: number
    page_size?: number
    q?: string
    direction?: 'IN' | 'OUT'
    enabled?: boolean
}

export interface DocTemplateCreatePayload {
    code: string
    name: string
    direction?: 'IN' | 'OUT'
    enabled?: boolean
    status_effect?: string | null
    status_restore?: string | null
    deadline_template_code?: string | null
    fee_draft_type?: string | null
    fee_item_list?: string | null
    need_reply?: boolean | null
    reply_to_template_code?: string | null
    input_fields?: string | null
}

export interface DocTemplateUpdatePayload {
    name?: string | null
    direction?: 'IN' | 'OUT' | null
    enabled?: boolean | null
    status_effect?: string | null
    status_restore?: string | null
    deadline_template_code?: string | null
    fee_draft_type?: string | null
    fee_item_list?: string | null
    need_reply?: boolean | null
    reply_to_template_code?: string | null
    input_fields?: string | null
}
```

**Rationale**: Fields map 1:1 to backend schemas. No renaming layer needed.

---

### File 2: `frontend/src/api/documents.ts` (MODIFY)

**Action**: Append DocTemplate CRUD functions at the end of the file.

**Add imports**: Import new types from `documents.types.ts`:
```typescript
import type {
    // ... existing ...
    DocTemplate,
    DocTemplateCreatePayload,
    DocTemplateListParams,
    DocTemplateUpdatePayload,
} from './documents.types'
```

**Add functions** (following TaskTemplate pattern from `tasks.ts` lines 142–157):

```typescript
// ── DocTemplate CRUD (FC1) ─────────────────────────────

export async function getDocTemplates(
    params: DocTemplateListParams = {}
): Promise<Pagination<DocTemplate>> {
    const { page = 1, page_size = 20, q, direction, enabled } = params
    const response = await http.get<Pagination<DocTemplate>>('/doc-templates', {
        params: {
            page,
            page_size,
            ...(q ? { q } : {}),
            ...(direction ? { direction } : {}),
            ...(enabled !== undefined ? { enabled } : {}),
        },
    })
    return response.data
}

export async function getDocTemplate(id: string): Promise<DocTemplate> {
    const response = await http.get<DocTemplate>(`/doc-templates/${id}`)
    return response.data
}

export async function createDocTemplate(
    data: DocTemplateCreatePayload
): Promise<DocTemplate> {
    const response = await http.post<DocTemplate>('/doc-templates', data)
    return response.data
}

export async function updateDocTemplate(
    id: string,
    data: DocTemplateUpdatePayload
): Promise<DocTemplate> {
    const response = await http.put<DocTemplate>(`/doc-templates/${id}`, data)
    return response.data
}
```

**Key differences from TaskTemplate pattern**:
- DocTemplates use **paginated** list (unlike TaskTemplates which return a flat array)
- No field mapping needed — backend fields match frontend types directly

---

### File 3: `frontend/src/modules/system/pages/DocTemplateList.vue` (NEW)

**Action**: Create new Vue SFC following `TaskTemplateList.vue` pattern exactly.

**Template structure** (following TaskTemplateList.vue):
- Page header: title "文件模板管理", count badge, "新增模板" button
- Error banner using `ApiErrorBanner`
- `el-table` with columns: code, name, direction, status_effect, deadline_template_code, fee_draft_type, need_reply, enabled (tag), actions (编辑 + toggle)
- `el-pagination` (since list is paginated — TaskTemplateList doesn't have this because task-templates aren't paginated; we need it here)
- Create/Edit dialog with form fields

**Table columns**:

| prop/label | width | Rendering |
|-----------|-------|-----------|
| code / 编码 | 120 | direct |
| name / 名称 | min-width 160 | direct |
| direction / 方向 | 80 | el-tag: IN=收文, OUT=发文 |
| status_effect / 状态变更 | 120 | `row.status_effect \|\| '—'` |
| deadline_template_code / 期限模板 | 140 | `row.deadline_template_code \|\| '—'` |
| fee_draft_type / 费用类型 | 120 | `row.fee_draft_type \|\| '—'` |
| need_reply / 需回复 | 80 | el-tag: true=是, false=否 |
| enabled / 状态 | 80 | el-tag success/info: 启用/停用 |
| 操作 | 160 | 编辑 button + toggle button |

**Dialog form fields** (all in `el-form` with `label-position="top"`):

| Field | Control | Required | Notes |
|-------|---------|----------|-------|
| code | el-input | YES | disabled on edit |
| name | el-input | YES | — |
| direction | el-select (IN/OUT) | NO | default: 'IN' |
| enabled | el-switch | NO | only shown on edit |
| status_effect | el-input | NO | — |
| status_restore | el-input | NO | — |
| deadline_template_code | el-select | NO | populated from `getTaskTemplates(true)` |
| fee_draft_type | el-input | NO | — |
| need_reply | el-switch | NO | — |
| reply_to_template_code | el-input | NO | — |
| fee_item_list | el-input type="textarea" rows=3 | NO | placeholder: JSON array |
| input_fields | el-input type="textarea" rows=3 | NO | placeholder: JSON object |

**Script setup** key implementation details:
- Import `getDocTemplates`, `createDocTemplate`, `updateDocTemplate` from `'../../../api/documents'`
- Import `getTaskTemplates` from `'../../../api/tasks'` (for dropdown)
- Import types: `DocTemplate` from `'../../../api/documents.types'`, `TaskTemplate` from `'../../../api/tasks.types'`
- Pagination: track `currentPage`, `pageSize`, `total` — bind `el-pagination`
- TaskTemplate list loaded `onMounted` for dropdown options
- Form reactive object with all fields, form validation rules for code + name
- `fetchTemplates()`, `openCreate()`, `openEdit(row)`, `handleSave()`, `handleToggleEnabled(row)` — same pattern as TaskTemplateList.vue

**Pagination implementation** (not in TaskTemplateList since task-templates aren't paginated):
```html
<el-pagination
  v-if="total > pageSize"
  :current-page="currentPage"
  :page-size="pageSize"
  :total="total"
  layout="total, prev, pager, next"
  @current-change="handlePageChange"
/>
```

---

### File 4: `frontend/src/router/index.ts` (MODIFY)

**Action**: Add route entry for DocTemplateList in the system routes section.

**Insert after** the `system/task-templates` route (line 204):

```typescript
{
    path: 'system/doc-templates',
    name: 'system_doc_templates',
    component: () => import('../modules/system/pages/DocTemplateList.vue'),
    meta: { requiredPerms: [Perms.SETTINGS_READ] }
},
```

**Permission**: Uses `SETTINGS_READ` — same as task-templates route.

---

### File 5: `frontend/src/constants/menu.ts` (MODIFY)

**Action**: Add menu item in the `settings` group, after `task_templates`.

**Insert after** the task_templates entry (line 59):

```typescript
{ key: 'doc_templates', label: '文件模板', icon: '📄', route: '/system/doc-templates', requiredPerms: [Perms.SETTINGS_READ] },
```

---

## 5. Interaction Flow

### List View
1. User navigates to 系统设置 → 文件模板
2. `onMounted`: calls `getDocTemplates({ page: 1, page_size: 20 })` + `getTaskTemplates(true)` in parallel
3. Table renders with pagination
4. Toggle enabled: calls `updateDocTemplate(id, { enabled: !current })`, refresh list

### Create Flow
1. User clicks "新增模板"
2. Dialog opens with blank form, direction defaults to 'IN'
3. User fills code (required), name (required), optional fields
4. `deadline_template_code` dropdown shows task templates (code as value, name as label)
5. Save → calls `createDocTemplate(payload)` → refresh list, close dialog

### Edit Flow
1. User clicks "编辑" on a row
2. Dialog opens with form pre-filled from row data
3. `code` field is disabled (not updatable per backend schema)
4. Save → calls `updateDocTemplate(id, payload)` → refresh list, close dialog

---

## 6. Integration with Existing Patterns

| Aspect | TaskTemplateList.vue Pattern | DocTemplateList.vue Adaptation |
|--------|------------------------------|-------------------------------|
| API calls | `getTaskTemplates()` flat array | `getDocTemplates()` paginated |
| Mapping | Direct — no mapper | Direct — no mapper |
| Dialog | Reactive form + rules | Same pattern |
| Toggle | `updateTaskTemplate(id, { enabled })` | `updateDocTemplate(id, { enabled })` |
| Error | `ApiErrorBanner` component | Same |
| Imports | Relative `../../../api/tasks` | Relative `../../../api/documents` |
| Extra data | — | Load `getTaskTemplates(true)` for dropdown |
| Pagination | None (flat array) | **Add el-pagination** |
| CSS | `.table-empty` scoped style | Same |

---

## 7. Acceptance Criteria Checklist

1. [ ] `DocTemplate`, `DocTemplateCreatePayload`, `DocTemplateUpdatePayload`, `DocTemplateListParams` types exist in `documents.types.ts`
2. [ ] `getDocTemplates()`, `getDocTemplate()`, `createDocTemplate()`, `updateDocTemplate()` functions exist in `documents.ts`
3. [ ] `DocTemplateList.vue` renders table with correct columns: code, name, direction, status_effect, deadline_template_code, fee_draft_type, need_reply, enabled
4. [ ] Create dialog opens with blank form, requires code + name
5. [ ] Edit dialog opens with pre-filled data, code field disabled
6. [ ] `deadline_template_code` dropdown populated from TaskTemplate list
7. [ ] Toggle enabled button works (calls update, refreshes list)
8. [ ] Pagination works for template list
9. [ ] Route `/system/doc-templates` exists and loads DocTemplateList.vue
10. [ ] Menu item "文件模板" appears under 系统设置 group
11. [ ] `npm run lint` passes
12. [ ] `npm run typecheck` passes
13. [ ] `npm run build` passes
14. [ ] No files outside the 5-file allowlist were modified

---

## 8. Risk / Issues Log

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R1 | `deadline_template_code` dropdown needs TaskTemplate data — requires cross-module API call | LOW | Reuse existing `getTaskTemplates(true)` from `tasks.ts` — already proven in FB4 |
| R2 | `fee_item_list` and `input_fields` are JSON strings — user could enter invalid JSON | LOW | These are admin-only fields; add placeholder text hinting at expected format. Backend stores as plain text, no validation. Out of scope for FC1 to add JSON validation. |
| R3 | Backend `DocTemplateUpdateIn` does NOT include `code` field (not updatable) | INFO | Frontend disables code input on edit — matches backend contract |
| R4 | Backend paginated list uses `PageResult[DocTemplateOut]` which returns `{ items, page, page_size, total }` — matches frontend `Pagination<T>` interface | INFO | No adaptation needed |
| R5 | `direction` enum is `IN`/`OUT` string — must match exactly | LOW | Use string literal type `'IN' | 'OUT'` matching backend `DocumentDirection` enum |

---

## 9. Task Decomposition

Tasks are already created in the task list. Execution order with dependencies:

```
T1 (types) ──┐
              ├── T3 (Vue page) ──┐
T2 (API fns) ─┘                   │
                                   ├── T7 (quality gate)
T4 (router) ───────────────────────┤
T5 (menu) ─────────────────────────┘
```

| Task | ID | Depends On | Estimated Scope |
|------|----|-----------|-----------------|
| T1: Add DocTemplate types to `documents.types.ts` | #2 | none | ~50 lines append |
| T2: Add DocTemplate CRUD functions to `documents.ts` | #3 | T1 (types import) | ~40 lines append + import update |
| T3: Create `DocTemplateList.vue` | #4 | T1, T2 | ~250 lines new file |
| T4: Add route to `router/index.ts` | #5 | none | ~5 lines insert |
| T5: Add menu item to `menu.ts` | #6 | none | ~1 line insert |
| T7: Quality gate (lint + typecheck + build) | #7 | T1–T5 | verification only |
| T8: Review report | #8 | T7 | read + verify |

**Parallelism opportunity**: T4 and T5 have no dependencies and can run in parallel with T1/T2. T3 depends on T1 and T2.

**Recommended execution**:
1. **Wave 1** (parallel): T1 + T2 + T4 + T5
2. **Wave 2** (sequential): T3 (depends on T1, T2)
3. **Wave 3**: T7 quality gate
4. **Wave 4**: T8 review

---

## Appendix: Key Source References

| File | Key Lines | What |
|------|-----------|------|
| `backend/app/modules/documents/api.py` | 51–113 | B1 DocTemplate endpoints |
| `backend/app/modules/documents/models.py` | 30–48 | DocTemplate ORM model |
| `backend/app/modules/documents/schemas.py` | 69–119 | DocTemplate Pydantic schemas |
| `backend/app/modules/documents/enums.py` | 6–8 | DocumentDirection enum |
| `backend/app/modules/documents/service.py` | 314–405 | DocTemplate CRUD service |
| `frontend/src/modules/system/pages/TaskTemplateList.vue` | 1–251 | Reference pattern |
| `frontend/src/api/tasks.ts` | 142–157 | TaskTemplate CRUD reference |
| `frontend/src/api/tasks.types.ts` | 53–85 | TaskTemplate types reference |
| `frontend/src/router/index.ts` | 181–205 | System routes section |
| `frontend/src/constants/menu.ts` | 55–61 | Settings menu group |
