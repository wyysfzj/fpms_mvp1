# FB1 Architect Plan — Task Detail Page + TaskLog View

## 1. FB1 Summary

**Goal**: Create the missing `/tasks/:id` detail page displaying task metadata, status actions (Close/Reopen/Cancel), and an audit log timeline (from backend A1's `GET /tasks/{id}/logs` API).

**Scope**: 5 files (3 modify, 2 new). No backend changes.

**Backend Dependency**: Backend Batch A1 — CONFIRMED COMPLETE (see Section 2).

---

## 2. Backend A1 Verification

### GET /tasks/{task_id} — CONFIRMED
- **Location**: `backend/app/modules/tasks/api.py:553-579`
- **Permission**: `Task.Read`
- **Response schema**: `TaskOut` (Pydantic model)
- **Response shape**:
```json
{
  "id": "string (UUID)",
  "case_id": "string | null",
  "document_id": "string | null",
  "task_template_id": "string | null",
  "title": "string",
  "base_date": "date | null",
  "due_date": "date",
  "internal_due_date": "date | null",
  "worker_id": "string | null",
  "supervisor_id": "string | null",
  "remark": "string | null",
  "status": "OPEN | DONE | CANCELLED",
  "done_at": "datetime | null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### GET /tasks/{task_id}/logs — CONFIRMED
- **Location**: `backend/app/modules/tasks/api.py:543-550`
- **Permission**: `Task.Read`
- **Response schema**: `list[TaskLogOut]`
- **Response shape** (each item):
```json
{
  "id": "string (UUID)",
  "task_id": "string",
  "action": "CREATE | UPDATE | ASSIGN | CLOSE | REOPEN | CANCEL | AUTO_CREATE | AUTO_CREATE_FROM_DOCUMENT | AUTO_WRITEOFF | STATUS_CHANGE",
  "from_status": "OPEN | DONE | CANCELLED | null",
  "to_status": "OPEN | DONE | CANCELLED | null",
  "remark": "string | null",
  "created_at": "datetime"
}
```

### Status Action Endpoints — CONFIRMED
- `POST /tasks/{id}/close` — body: `{ remark?: string }` — Permission: `Task.Action`
- `POST /tasks/{id}/reopen` — body: `{ remark?: string }` — Permission: `Task.Action`
- `POST /tasks/{id}/cancel` — body: `{ remark?: string }` — Permission: `Task.Action`

Frontend already has `closeTask()`, `reopenTask()`, `cancelTask()` wrappers in `tasks.ts`.

### Known Gap
- **`created_by` not in TaskLogOut**: The `AuditMixin` (mixins.py:34) provides `created_by` on the ORM model, but `TaskLogOut` schema (schemas.py:91-100) does NOT expose it. The spec says logs should show "by {username}" but the backend doesn't return it.
- **Mitigation**: Add `created_by` as optional field in frontend type. It will be `undefined` for now. When backend adds it to the schema, the UI will automatically display it.

---

## 3. File Allowlist

| # | File | Action | Description |
|---|------|--------|-------------|
| 1 | `frontend/src/api/tasks.types.ts` | MODIFY | Add `TaskDetail`, `TaskLog` type definitions |
| 2 | `frontend/src/api/tasks.ts` | MODIFY | Add `getTask(id)`, `getTaskLogs(taskId)` API functions |
| 3 | `frontend/src/modules/tasks/pages/TaskDetail.vue` | NEW | Full task detail page with tabs |
| 4 | `frontend/src/modules/tasks/components/TaskLogTimeline.vue` | NEW | Audit log timeline component |
| 5 | `frontend/src/router/index.ts` | MODIFY | Add `/tasks/:id` route |

---

## 4. Current State Analysis

### `frontend/src/api/tasks.ts` (112 lines)
- **Existing functions**: `getTasks()`, `createTask()`, `closeTask()`, `reopenTask()`, `cancelTask()`, `getTodayReminders()`
- **Missing**: `getTask(id)` — single task fetch, `getTaskLogs(taskId)` — log fetch
- **Pattern**: Uses internal `BackendTask` interface for mapping, `mapTask()` for transformation
- **Note**: `BackendTask` doesn't have `base_date`, `internal_due_date`, `done_at`, `task_template_id` — detail endpoint returns more fields

### `frontend/src/api/tasks.types.ts` (35 lines)
- **Existing types**: `Task` (list item), `TaskListParams`, `TaskCreatePayload`
- **Missing**: `TaskDetail` (full detail response), `TaskLog` (audit log entry)
- **Note**: Current `Task` type is a frontend-mapped shape (e.g., `assigned_to` instead of `worker_id`). For detail, we should add a richer type.

### `frontend/src/router/index.ts` (228 lines)
- **Existing task routes**: `/tasks` (list), `/tasks/new` (create), `/tasks/today` (reminders)
- **Missing**: `/tasks/:id` (detail)
- **Pattern**: Uses lazy imports, `meta: { requiredPerms: [...] }`, `Perms.*` constants
- **Note**: Must place `/tasks/:id` AFTER `/tasks/new` and `/tasks/today` to avoid route conflicts

### `frontend/src/modules/tasks/` directory
- **Existing**: `pages/` (TaskList.vue, TaskCreate.vue, TodayReminders.vue), `docs/`
- **Missing**: `components/` directory (needs to be created for TaskLogTimeline.vue)

---

## 5. Implementation Specification

### 5.1 tasks.types.ts — Add Types

Add after existing types:

```typescript
/**
 * Full task detail from GET /tasks/{id}
 * Extends basic Task with additional backend fields
 */
export interface TaskDetail {
    id: string
    case_id: string | null
    document_id: string | null
    task_template_id: string | null
    title: string
    base_date: string | null
    due_date: string
    internal_due_date: string | null
    worker_id: string | null
    supervisor_id: string | null
    remark: string | null
    status: string
    done_at: string | null
    created_at: string
    updated_at: string
}

/**
 * Task audit log entry from GET /tasks/{id}/logs
 */
export interface TaskLog {
    id: string
    task_id: string
    action: string
    from_status: string | null
    to_status: string | null
    remark: string | null
    created_at: string
    created_by?: string  // AuditMixin field — not yet in backend schema
}
```

### 5.2 tasks.ts — Add API Functions

Add two functions at the end of the file:

```typescript
/**
 * Get a single task by ID
 */
export async function getTask(id: string): Promise<TaskDetail> {
    const response = await http.get<TaskDetail>(`/tasks/${id}`)
    return response.data
}

/**
 * Get audit logs for a task
 */
export async function getTaskLogs(taskId: string): Promise<TaskLog[]> {
    const response = await http.get<TaskLog[]>(`/tasks/${taskId}/logs`)
    return response.data
}
```

**Note**: `getTask()` returns raw backend shape (`TaskDetail`) without mapping — the detail page works directly with backend field names (worker_id, supervisor_id) rather than the mapped `Task` type.

Import `TaskDetail` and `TaskLog` from `./tasks.types`.

### 5.3 TaskDetail.vue — New Detail Page

**Location**: `frontend/src/modules/tasks/pages/TaskDetail.vue`

**Layout Structure** (following CaseDetail.vue pattern):

```
┌──────────────────────────────────────────┐
│ Header: ← 返回                           │
├──────────────────────────────────────────┤
│ [Error Banner — if error]                │
│ [Loading Skeleton — if loading]          │
├──────────────────────────────────────────┤
│ Task Header:                             │
│   Title: {title}            [Status Tag] │
│   案件: {case_id} (link)                  │
├──────────────────────────────────────────┤
│ Tab: 概览 │ Tab: 操作日志                  │
├──────────────────────────────────────────┤
│ Overview Tab:                            │
│   el-descriptions (2-column):            │
│     状态: {status text}                   │
│     到期日: {due_date}                    │
│     内部期限: {internal_due_date}          │
│     基准日: {base_date}                   │
│     执行人: {worker_id}                   │
│     监督人: {supervisor_id}               │
│     完成时间: {done_at}                   │
│     创建时间: {created_at}                │
│     更新时间: {updated_at}                │
│   备注: {remark}                          │
│                                          │
│   Actions: [关闭] [重新打开] [取消]        │
├──────────────────────────────────────────┤
│ Audit Log Tab:                           │
│   <TaskLogTimeline :task-id="id" />      │
├──────────────────────────────────────────┤
│ Empty State (if not found)               │
└──────────────────────────────────────────┘
```

**Script Details**:
- Imports: `ref, computed, onMounted, onBeforeUnmount` from vue
- Imports: `useRoute, useRouter` from vue-router
- Imports: `getTask` from `../../../api/tasks`
- Imports: `closeTask, reopenTask, cancelTask` from `../../../api/tasks`
- Imports: `TaskDetail` type from `../../../api/tasks.types`
- Imports: `ApiError` type from `../../../api/types`
- Imports: `ApiErrorBanner` from `../../../components/errors/ApiErrorBanner.vue`
- Imports: `TaskLogTimeline` from `../components/TaskLogTimeline.vue`
- Imports: `usePageContext` from `../../../stores/pageContext`
- Imports: `getTaskStatusText` from `../../../constants/displayText`
- Uses `ElMessageBox.confirm()` for action confirmation dialogs
- Uses `ElMessage.success()` for success notifications

**Status-based action visibility**:
- `OPEN` → show [关闭] and [取消]
- `DONE` → show [重新打开]
- `CANCELLED` → show [重新打开]

**Case link**: If `case_id` exists, render `<router-link :to="'/cases/' + task.case_id">` with case_id text.

**Chinese Labels** needed (add to `labels.zh.ts` if not already present — BUT labels.zh.ts is NOT in allowlist, so use inline strings following the pattern of existing pages that use ZH, or add a `taskDetail` section to ZH):

> **Decision**: Since `labels.zh.ts` is NOT in the file allowlist, use inline Chinese strings directly in the template. This is consistent with how `CaseTasksTab.vue` uses inline Chinese ("任务记录", "标题", etc.).

Inline labels to use:
- 任务详情 (page title / breadcrumb)
- 概览 (Overview tab)
- 操作日志 (Audit Log tab)
- 状态 (Status)
- 到期日 (Due Date)
- 内部期限 (Internal Due)
- 基准日 (Base Date)
- 执行人 (Worker)
- 监督人 (Supervisor)
- 完成时间 (Done At)
- 创建时间 (Created)
- 更新时间 (Updated)
- 备注 (Remark)
- 关闭 (Close)
- 重新打开 (Reopen)
- 取消 (Cancel)
- 未找到任务 (Task Not Found)
- 请求的任务不存在。 (Task not found message)

### 5.4 TaskLogTimeline.vue — New Component

**Location**: `frontend/src/modules/tasks/components/TaskLogTimeline.vue`

**Props**: `{ taskId: string }`

**Template Structure**:
```html
<el-timeline>
  <el-timeline-item
    v-for="log in logs"
    :key="log.id"
    :timestamp="formatTime(log.created_at)"
    placement="top"
  >
    <div class="log-entry">
      <span class="log-action">{{ actionText(log.action) }}</span>
      <span v-if="log.from_status || log.to_status" class="log-transition">
        {{ statusText(log.from_status) }} → {{ statusText(log.to_status) }}
      </span>
      <span v-if="log.created_by" class="log-actor">by {{ log.created_by }}</span>
      <p v-if="log.remark" class="log-remark">{{ log.remark }}</p>
    </div>
  </el-timeline-item>
</el-timeline>
```

**Script**:
- Imports: `ref, onMounted` from vue
- Imports: `getTaskLogs` from `../../../api/tasks`
- Imports: `TaskLog` type from `../../../api/tasks.types`
- Imports: `getTaskStatusText` from `../../../constants/displayText`
- `actionText(action)`: Map action enum to Chinese text
  - CREATE → 创建, UPDATE → 更新, ASSIGN → 分配, CLOSE → 关闭, REOPEN → 重新打开, CANCEL → 取消, AUTO_CREATE → 自动创建, AUTO_CREATE_FROM_DOCUMENT → 文档自动创建, AUTO_WRITEOFF → 自动核销, STATUS_CHANGE → 状态变更
- `statusText(status)`: Use `getTaskStatusText()` from displayText.ts
- `formatTime(ts)`: Simple date formatting (e.g., `new Date(ts).toLocaleString('zh-CN')`)

**States**: `logs: ref<TaskLog[]>([])`, `loading: ref(true)`

### 5.5 Router Change

**Location**: `frontend/src/router/index.ts`

Add after the `tasks/today` route (line 90), before `fees/drafts`:

```typescript
{
  path: 'tasks/:id',
  name: 'task_detail',
  component: () => import('../modules/tasks/pages/TaskDetail.vue'),
  meta: { requiredPerms: [Perms.TASKS_READ] }
},
```

**IMPORTANT**: Place AFTER `/tasks/new` and `/tasks/today` to avoid route conflicts (`:id` wildcard would match "new" and "today" if placed first).

---

## 6. Pattern Reference — CaseDetail.vue

The TaskDetail.vue should follow these patterns from CaseDetail.vue:

| Pattern | CaseDetail.vue | TaskDetail.vue |
|---------|---------------|----------------|
| Container class | `page-container focus-reading-page case-detail-page` | `page-container` |
| Back button | `el-button text @click="goBack"` with ← icon | Same pattern |
| Error display | `ApiErrorBanner` component | Same |
| Loading state | `el-skeleton :rows="10" animated` | Same |
| Content guard | `v-else-if="caseData"` | `v-else-if="task"` |
| Tabs | `el-tabs v-model="activeTab"` | Same (2 tabs) |
| Metadata display | Custom `.info-grid` divs | `el-descriptions` (per spec) |
| Breadcrumb | `pageContext.setBreadcrumb(...)` | Same |
| Cleanup | `onBeforeUnmount(() => pageContext.clear())` | Same |
| Status display | `getStatusTagClass()` + tag | `getTaskStatusText()` + el-tag |
| Imports | Relative paths (`../../../api/...`) | Same |

---

## 7. Chinese Label Inventory

Labels used inline in TaskDetail.vue:
- 任务详情, 概览, 操作日志, 状态, 到期日, 内部期限, 基准日
- 执行人, 监督人, 完成时间, 创建时间, 更新时间, 备注
- 关闭, 重新打开, 取消
- 未找到任务, 请求的任务不存在。
- 确定要关闭此任务吗？ / 确定要重新打开此任务吗？ / 确定要取消此任务吗？
- 操作成功

Labels used in TaskLogTimeline.vue:
- 创建, 更新, 分配, 关闭, 重新打开, 取消, 自动创建, 文档自动创建, 自动核销, 状态变更
- 加载中..., 暂无操作日志

Labels already in labels.zh.ts (reusable):
- `ZH.common.back` → 返回
- `ZH.taskList.close` → 关闭
- `ZH.taskList.reopen` → 重新打开
- `ZH.taskList.cancel` → 取消
- `ZH.taskList.closeConfirm` / `closeTitle` / etc. → Confirmation messages

**Recommendation**: Use `ZH.taskList.*` for shared labels (close, reopen, cancel, confirmations). Use inline strings for task-detail-specific labels. Since labels.zh.ts is not in the allowlist, adding a `taskDetail` section is not possible.

---

## 8. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| `created_by` missing from TaskLogOut | LOW | Add optional field in FE type; show "by {id}" when available. Timeline just omits actor for now. |
| Task `remark` field — model doesn't have explicit column but service/schema references it | LOW | Backend already handles this (returns it in TaskOut). Frontend just displays what backend sends. |
| `labels.zh.ts` not in allowlist | LOW | Use inline Chinese strings + reuse existing `ZH.taskList.*` and `ZH.common.*` |
| Status tag styling | LOW | Reuse `getTaskStatusText()` from displayText.ts. For el-tag type, use inline mapping (OPEN→warning, DONE→success, CANCELLED→info). |
| No `case_no` in TaskOut response | MEDIUM | GET /tasks/{id} returns `case_id` but not `case_no`. The detail page will show case_id as link text. If case_no is desired, it would require either (a) a second API call to GET /cases/{id}, or (b) backend enhancement. For MVP, showing the link to the case is sufficient. |
| `worker_id` / `supervisor_id` are UUIDs, not names | MEDIUM | Same as case_no issue — backend returns IDs not names. For MVP, display the UUID (truncated) or just show the field. A future enhancement can resolve user names. |

---

## 9. Execution Order

1. **tasks.types.ts** — Add `TaskDetail` and `TaskLog` interfaces
2. **tasks.ts** — Add `getTask()` and `getTaskLogs()` functions (depends on types)
3. **TaskLogTimeline.vue** — Create component (depends on API functions)
4. **TaskDetail.vue** — Create page (depends on API functions + component)
5. **router/index.ts** — Add route (depends on page existing)

All 5 steps can be done by a single impl agent sequentially.

---

## 10. Quality Gate

```bash
cd frontend && npm run lint && npm run typecheck && npm run build
```

All three must pass before the task is considered complete.

---

## 11. Acceptance Criteria Checklist

- [ ] `/tasks/:id` route registered and loads TaskDetail.vue
- [ ] TaskDetail.vue fetches task on mount, displays all metadata fields in el-descriptions
- [ ] Status tag shows correct Chinese text (待处理/已完成/已取消)
- [ ] Status actions (关闭/重新打开/取消) visible based on current status
- [ ] Actions use ElMessageBox.confirm() before executing
- [ ] Actions call existing closeTask/reopenTask/cancelTask APIs
- [ ] After action success, task data refreshes
- [ ] Case link navigates to `/cases/{case_id}` when case_id exists
- [ ] Audit Log tab renders TaskLogTimeline component
- [ ] TaskLogTimeline fetches logs on mount and displays as el-timeline
- [ ] Each log entry shows: timestamp, action text, status transition, remark
- [ ] Loading and error states handled correctly
- [ ] PageContext breadcrumb set on mount, cleared on unmount
- [ ] Quality gate passes: `npm run lint && npm run typecheck && npm run build`
