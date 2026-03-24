# Batch FC6 — 01 Architect Plan

## Scope Summary

### What Changes
1. **`dashboard.api.ts`** — Simplify `fetchEnrichedTasks()` by removing the unnecessary `getCases()` batch-fetch (lines 119-131) and using `task.client_name` directly from B6 task response. Document unallocated payments metric as known limitation (already documented in comments).

### What Does NOT Change
- **`fetchDashboardKpi()`** — Already uses `.total` from paginated responses (lines 32-38). No changes needed.
- **`Dashboard.vue`** — No changes needed. All wiring is correct. PipeCard displays, loading states, error handling all working.
- **`ActionCenter.vue`** — Already shows `client_name` (line 27), `EnrichedTask` interface already has `client_name` field (line 49). No changes needed.
- **`fetchPipelineKpi()`** — Urgent task counting logic (lines 70-76) is correct. The unallocated payments issue (line 83 sums ALL payments) cannot be fixed without backend changes; it's already documented with comments on lines 81-82.

---

## Change 1: Simplify `fetchEnrichedTasks()` in `dashboard.api.ts`

### Problem
Lines 119-131 fetch ALL cases (`page_size=200`) via `getCases()` just to build a `clientNameMap` for resolving `client_name` from `case_id`. Since backend batch B6, the task API response already includes `client_name` directly on each task object.

### Current Code (lines 114-147)
```typescript
export async function fetchEnrichedTasks(): Promise<EnrichedTask[]> {
    // Fetch open tasks (backend now returns case_no)
    const tasksRes = await getTasks({ page: 1, page_size: 10, status: 'OPEN' })
    const tasks = tasksRes.items

    // Collect unique case_ids to batch-fetch client_names
    const caseIds = [...new Set(tasks.map(t => t.case_id).filter(Boolean))] as string[]
    const clientNameMap = new Map<string, string>()

    if (caseIds.length > 0) {
        // Fetch cases to get client_ids and client_names
        const casesRes = await getCases({ page: 1, page_size: 200 })
        for (const c of casesRes.items) {
            if (c.client_name) {
                clientNameMap.set(c.id, c.client_name)
            }
        }
    }

    return tasks.map(task => {
        const deadline = computeDeadline(task.due_date)
        return {
            id: task.id,
            title: task.title,
            case_id: task.case_id,
            case_no: task.case_no,
            client_name: task.case_id ? clientNameMap.get(task.case_id) : undefined,
            has_document: !!task.document_id,
            has_fee: false, // fee linkage not available in task response
            deadline_text: deadline.text,
            deadline_class: deadline.class,
        }
    })
}
```

### After (simplified)
```typescript
export async function fetchEnrichedTasks(): Promise<EnrichedTask[]> {
    const tasksRes = await getTasks({ page: 1, page_size: 10, status: 'OPEN' })

    return tasksRes.items.map(task => {
        const deadline = computeDeadline(task.due_date)
        return {
            id: task.id,
            title: task.title,
            case_id: task.case_id,
            case_no: task.case_no,
            client_name: task.client_name,
            has_document: !!task.document_id,
            has_fee: false,
            deadline_text: deadline.text,
            deadline_class: deadline.class,
        }
    })
}
```

### Specific Edits
1. **Remove lines 119-131** — The entire `caseIds` / `clientNameMap` / `getCases()` block
2. **Remove line 117** — `const tasks = tasksRes.items` (inline it as `tasksRes.items.map(...)`)
3. **Change line 140** — `client_name: task.case_id ? clientNameMap.get(task.case_id) : undefined` → `client_name: task.client_name`
4. **Update comment on line 115** — Remove reference to case batch-fetching

### Import Cleanup Check
- `getCases` (line 2) — **KEEP**: Still used by `fetchWorkflowStats()` (line 240)
- `Case` type (line 6) — **KEEP**: Still used by `WorkflowStats` interface (line 236)
- No imports need removal

### Benefits
- Eliminates 1 extra API call (`GET /api/v1/cases?page_size=200`) on every dashboard load
- Removes O(n) map construction logic
- Simpler, more maintainable code

---

## Change 2: Unallocated Payments Metric — Document as Known Limitation

### Problem
`fetchPipelineKpi()` line 83 sums ALL payment amounts as "unallocated payments". The correct metric should only sum payments without full offset. However, the backend payment list API does not expose an `offset_status` or `balance` field that could be used for filtering.

### Decision: NO CODE CHANGE — Already Documented
Lines 81-82 already contain adequate documentation:
```typescript
// MVP限制: 付款总额包含所有付款记录，非仅未核销部分。
// 系统暂无 offset 状态字段可用于过滤真正未分配的付款。
```

The PipeCard label in Dashboard.vue (line 52) shows `ZH.pipeline.unallocated` — the label is cosmetically correct. The underlying value is a known approximation.

**Rationale**: Fixing this requires a backend change (adding `balance` or `offset_status` to payment response schema), which is out of FC6 scope. The existing comments correctly document the limitation.

---

## Change 3: Dashboard.vue — NO CHANGES NEEDED

**Justification**:
- PipeCard bindings (lines 27-54) are correctly wired to `pipe` reactive ref
- Loading skeletons (lines 22-25) properly gate content display
- `onMounted` parallel fetch pattern (lines 175-197) is optimal
- Error handling (lines 178, 183, 188, 193) catches per-section failures
- `formatMoney()` helper (lines 155-160) uses correct locale formatting
- All component imports and type imports are correct

---

## Change 4: ActionCenter.vue — NO CHANGES NEEDED

**Justification**:
- `client_name` is already displayed on line 27: `<span v-if="task.client_name">{{ task.client_name }}</span>`
- `EnrichedTask` interface (lines 44-54) already includes `client_name?: string` (line 49)
- Template structure (case_no tag + title + client_name row) is correct
- Router navigation on click (lines 63-66) works properly

---

## Acceptance Criteria

- [ ] **AC1**: `fetchEnrichedTasks()` no longer calls `getCases()` — only calls `getTasks()`
- [ ] **AC2**: `client_name` in enriched tasks is sourced from `task.client_name` (direct from B6 response), not from a case lookup map
- [ ] **AC3**: Dashboard loads with all KPI cards, action center tasks display correctly with `client_name` visible
- [ ] **AC4**: No regressions — `fetchPipelineKpi()`, `fetchWorkflowStats()`, `fetchFinanceData()` remain unchanged
- [ ] **AC5**: Quality gate passes: `npm run lint && npm run typecheck && npm run build`
- [ ] **AC6**: Unallocated payments limitation is documented (existing comments preserved)

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `task.client_name` is undefined for some tasks | Low (B6 populates it) | Graceful: `v-if="task.client_name"` in ActionCenter already handles undefined |
| Breaking other dashboard sections | Very Low | Only `fetchEnrichedTasks()` is modified; other functions untouched |
| Type errors | Very Low | `Task.client_name` is already typed as `string \| undefined` in `tasks.types.ts` line 11 |

---

## Implementation Notes for Agent

1. The edit is surgical: replace the body of `fetchEnrichedTasks()` (lines 114-147) with the simplified version
2. Do NOT touch any other function in the file
3. Do NOT modify imports (getCases and Case are still needed by other functions)
4. Run quality gate after edit: `cd frontend && npm run lint && npm run typecheck && npm run build`
