# FPMS MVP1 Frontend Enhancement Plan — Claude FE Edition

> **Author**: Claude (synthesized from codebase audit + MVP1 scope + FPMS SPEC 2.0)
> **Date**: 2026-02-24
> **Goal**: (1) Close frontend MVP1 scope gaps, (2) Align FE with backend enhancement batches A1–B6, (3) Provide SPEC 2.0 interface stubs where template data unavailable
> **Discipline**: Strict sequential phases. Each batch MUST pass quality gate before next batch starts.

---

## 0. Execution Discipline

### 0.1 Iron Rules

1. **Phase order is MANDATORY** — FA before FB before FC
2. **Quality gate per batch** — every batch ends with `npm run lint && npm run typecheck && npm run build` passing
3. **File Allowlist enforced** — each batch lists exactly which files may be modified/created. If additional files needed, STOP and create a new atomic fix task
4. **No backend modifications** — this plan is FE-only. Backend changes are in `Claude_enhance.md`
5. **No scope creep** — frozen features stay frozen (see Section 0.3)
6. **Evidence required** — every batch records pass/fail of quality gate + manual smoke results
7. **Relative imports only** — no `@/` alias. Use `../../api/http` etc.
8. **CSS tokens mandatory** — use `var(--color-primary)` etc. from `variables.css`. No inline hex colors
9. **Element Plus only** — no additional UI libraries. Use `el-table`, `el-form`, `el-select`, etc.
10. **Chinese labels** — all user-facing text from `labels.zh.ts` or inline Chinese strings (demo-mode compatible)

### 0.2 Quality Gate (run after every batch)

```bash
cd frontend
npm run lint          # ESLint — must pass clean
npm run typecheck     # vue-tsc --noEmit — must pass
npm run build         # Vite production build — must succeed
npm run dev &         # Start dev server
sleep 5
curl -sf http://localhost:5173  # Dev server responds
kill %1
```

### 0.3 Frozen Features (NOT in any FE batch)

| Feature | Reason |
|---------|--------|
| PCT case type UI | MVP1 out-of-scope |
| Annual fee batch wizard | MVP1 out-of-scope |
| Invalidation/litigation forms | MVP1 out-of-scope |
| Dunning letter generation | MVP1 out-of-scope |
| Commission calculation UI | MVP1 out-of-scope |
| Template builder/editor | MVP1 out-of-scope (file-based only) |
| Full-text search / Elasticsearch | MVP1 out-of-scope |
| User/Role management pages | Post-MVP1 (admin-only, via seed) |
| PWA / offline mode | Post-MVP1 |
| Excel/PDF export | Post-MVP1 (nice-to-have, not in scope) |

### 0.4 Backend Dependency Matrix

| FE Batch | Requires Backend Batch | Key APIs Consumed |
|----------|----------------------|-------------------|
| FA0 | None (existing) | All existing endpoints |
| FA1 | None (existing) | GET /documents, GET /tasks, GET /fees/drafts (filtered by case_id) |
| FA2 | None (existing) | Existing list endpoints + filter params |
| FB1 | **A1** (TaskTemplate + TaskLog) | GET /task-templates, GET /tasks/{id}/logs |
| FB2 | **A2** (Client Address/Contact) | GET/POST/PUT/DELETE /clients/{id}/addresses, /contacts |
| FB3 | **A3** (Case Field Expansion) | Extended CaseCreate/CaseDetail schemas |
| FB4 | **A1 + A4** (TaskTemplate + SystemParam) | GET /task-templates, PUT /system/params |
| FB5 | **A5** (Advanced Case Search) | GET /cases with new filter params |
| FC1 | **B1** (DocTemplate Enhancement) | GET/POST/PUT /doc-templates |
| FC2 | **B2** (Reply Chain) | Extended Document schemas (reply_to_id, need_reply) |
| FC3 | **B4** (FeeRate Dimensions) | Extended FeeRate schemas |
| FC4 | **B5** (Offset Reversal) | POST /offsets/{id}/reverse, extended CaseReceipt |
| FC5 | **B6** (Search Enhancement) | Extended list responses (client_name, case_no joins) |
| FC6 | None (FE-only polish) | Existing aggregation endpoints |

---

## 1. Current Frontend Reality (Audit Results)

### Already Implemented (working)

| Module | Pages | Status |
|--------|-------|--------|
| Auth | Login.vue | Complete |
| Dashboard | Dashboard.vue + 9 components | Functional (fragile KPIs) |
| Cases | CaseList, CaseCreate, CaseEdit, CaseDetail | Detail has 4 stubbed tabs |
| Documents | DocumentList, DocumentCreate, DocumentEdit, DocumentDetail | Complete CRUD |
| Tasks | TaskList, TaskCreate, TodayReminders | **No TaskDetail page** |
| Fees | FeeDraftList, FeeDraftCreate, FeeDraftDetail, FeeRates | Complete |
| Billing | BillList, BillCreate, BillDetail, PaymentList, PaymentCreate | Complete |
| Clients | ClientList (2 routes), ClientForm (create/edit) | **No ClientDetail page** |
| System | SystemParams, TemplateList, LetterheadList | Complete |

### Actually Missing (verified against code)

| Gap | Priority | Phase |
|-----|----------|-------|
| CaseDetail: 4 tabs stubbed (Claims, OfficialDocs, Fees, Tasks) | P0 | FA1 |
| TaskDetail page (`/tasks/:id`) does not exist | P0 | FB1 |
| ClientDetail page (`/clients/:id`) does not exist | P0 | FB2 |
| No TaskTemplate admin UI | P0 | FB4 |
| No TaskLog display (audit trail) | P0 | FB1 |
| No Client Address/Contact management UI | P1 | FB2 |
| Case create/edit missing 15 SPEC fields (A3) | P1 | FB3 |
| No advanced case search filters (client, date range, type) | P1 | FB5 |
| No DocTemplate admin UI | P1 | FC1 |
| No document reply chain display | P1 | FC2 |
| No template selection in document create | P1 | FC2 |
| No fee rate dimension columns in rate list | P2 | FC3 |
| No offset reversal button in billing | P2 | FC4 |
| No client_name enrichment in task/document lists | P2 | FC5 |
| Dashboard KPIs use client-side aggregation (fragile) | P2 | FC6 |
| List filter UX inconsistency (some pages lack filters) | P2 | FA2 |

---

## 2. Batch Execution Plan

### Dependency Graph

```
FA0 (FE Baseline Smoke)
 └─→ FA1 (Case Detail Tab Completion)
      └─→ FA2 (List UX Polish)
           └─→ ═══ PHASE A DONE (no backend dependency) ═══
                └─→ FB1 (TaskDetail + TaskLog)          [needs BE A1]
                     └─→ FB2 (ClientDetail + Addr/Contact) [needs BE A2]
                          └─→ FB3 (Case Field Expansion)   [needs BE A3]
                               └─→ FB4 (TaskTemplate + SysParam Admin) [needs BE A1+A4]
                                    └─→ FB5 (Case Search Filters)   [needs BE A5]
                                         └─→ ═══ FE MVP1 SCOPE GATE ═══
                                              └─→ FC1 (DocTemplate Admin)      [needs BE B1]
                                                   └─→ FC2 (Doc Reply Chain + Template Select) [needs BE B2]
                                                        └─→ FC3 (FeeRate Dimensions)   [needs BE B4]
                                                             └─→ FC4 (Offset Reversal)  [needs BE B5]
                                                                  └─→ FC5 (List Enrichment) [needs BE B6]
                                                                       └─→ FC6 (Dashboard Polish)
                                                                            └─→ ═══ FE SPEC GATE ═══
```

---

## Batch FA0 — FE Baseline Smoke Test

**Goal**: Verify all existing frontend pages load and render without console errors. No code changes.

**Duration**: ~30 min. NO code changes.

### Verification Script

```bash
# Prerequisites: backend running on :8000, frontend dev on :5173
cd frontend && npm run dev &
sleep 5

# Manual smoke checklist:
# 1. Open http://localhost:5173 → redirects to /login
# 2. Login with admin/admin123 → dashboard loads with KPI cards
# 3. Navigate: Cases → list renders, Create → form works
# 4. Navigate: Documents → list renders, Create → form works
# 5. Navigate: Tasks → list renders, Create → form works, Today → loads
# 6. Navigate: Fees → Drafts list renders, Rates list renders
# 7. Navigate: Billing → Bills list, Payments list
# 8. Navigate: Clients → list renders, New → form works
# 9. Navigate: System → Params, Templates, Letterheads
# 10. Open browser DevTools console → no red errors
```

### Success Criteria

- [ ] All 9 modules' pages load without JS errors
- [ ] Login→Dashboard flow works
- [ ] CRUD operations work for at least Cases and Tasks
- [ ] DevTools console shows no uncaught errors

### Agent Prompt (FA0)

```
You are verifying the FPMS MVP1 frontend baseline.

## Context
FPMS frontend: Vue 3 + TypeScript + Element Plus + Vite.
Backend must be running at http://localhost:8000 (admin/admin123).
Frontend dev server at http://localhost:5173.

## Your Task
1. Start frontend dev server: cd frontend && npm run dev
2. Run quality gate: npm run lint && npm run typecheck && npm run build
3. Open each page listed above and verify no console errors
4. Record results in artifacts/FA0_plan/summary.md

## Constraints
- Do NOT modify any source files
- Only fix build/lint issues if they block the quality gate
- Record all findings
```

---

## Batch FA1 — Case Detail Tab Completion

**Goal**: Replace the 4 stubbed tabs in CaseDetail.vue with actual data views, using existing API endpoints filtered by `case_id`.

### Scope

**Files Modified:**

| File | Change |
|------|--------|
| `frontend/src/modules/cases/pages/CaseDetail.vue` | Replace stub content in 4 tabs |
| `frontend/src/modules/cases/components/CaseDocumentsTab.vue` | NEW: filtered document list |
| `frontend/src/modules/cases/components/CaseTasksTab.vue` | NEW: filtered task list |
| `frontend/src/modules/cases/components/CaseFeesTab.vue` | NEW: filtered fee draft list |
| `frontend/src/modules/cases/components/CaseClaimsTab.vue` | NEW: placeholder with case applicants/inventors |

**Tab implementations:**

1. **Official Docs tab** → `CaseDocumentsTab.vue`
   - Call `GET /api/v1/documents?case_id={caseId}` (existing API supports this filter)
   - Show table: direction (IN/OUT badge), title, doc_date, created_at
   - "Register Document" button → navigates to `/documents/new?case_id={caseId}`

2. **Tasks tab** → `CaseTasksTab.vue`
   - Call `GET /api/v1/tasks?case_id={caseId}` (existing API supports this filter)
   - Show table: title, status (tag), due_date, worker
   - Status action buttons (Close/Reopen) inline

3. **Fees tab** → `CaseFeesTab.vue`
   - Call `GET /api/v1/fees/drafts?case_id={caseId}` (existing API supports this filter)
   - Show table: draft_type, status, currency, total_amount
   - "Create Fee Draft" button → `/fees/drafts/new?case_id={caseId}`

4. **Claims tab** → `CaseClaimsTab.vue`
   - Display applicants and inventors from case detail response (already loaded)
   - Table layout for each: seq, name_cn, name_en
   - Read-only display (editing via case edit page)

**Non-scope**: No new API calls beyond existing filtered lists. No inline editing in tabs.

### Acceptance Criteria

- [ ] All 4 tabs show real data (not placeholder text)
- [ ] Docs tab shows documents linked to this case
- [ ] Tasks tab shows tasks linked to this case with status tags
- [ ] Fees tab shows fee drafts linked to this case
- [ ] Claims tab shows applicants and inventors
- [ ] "Create" buttons navigate to correct forms with case_id pre-filled
- [ ] Quality gate passes

### Agent Team Prompt (FA1)

```
You are implementing Batch FA1 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
FPMS frontend: Vue 3 + TypeScript + Element Plus.
CaseDetail.vue at frontend/src/modules/cases/pages/CaseDetail.vue has 6 tabs.
Tabs 2-5 (Claims, Official Docs, Fees, Tasks) currently show placeholder text "📄 待实现".
The backend already supports filtering by case_id on documents, tasks, and fee drafts.

## Your Task
1. Read CaseDetail.vue to understand the current tab structure
2. Create 4 new components in frontend/src/modules/cases/components/:
   - CaseDocumentsTab.vue — fetches GET /documents?case_id={props.caseId}
   - CaseTasksTab.vue — fetches GET /tasks?case_id={props.caseId}
   - CaseFeesTab.vue — fetches GET /fees/drafts?case_id={props.caseId}
   - CaseClaimsTab.vue — displays props.applicants and props.inventors
3. Import and use these components in CaseDetail.vue, replacing stub content
4. Each tab component receives caseId as prop and fetches its own data on mount
5. Use el-table for display, el-tag for status badges, el-button for actions

## File Allowlist (ONLY modify/create these)
- frontend/src/modules/cases/pages/CaseDetail.vue (modify)
- frontend/src/modules/cases/components/CaseDocumentsTab.vue (new)
- frontend/src/modules/cases/components/CaseTasksTab.vue (new)
- frontend/src/modules/cases/components/CaseFeesTab.vue (new)
- frontend/src/modules/cases/components/CaseClaimsTab.vue (new)

STOP if additional files are required — create a new atomic fix task.

## API Endpoints (existing, no changes needed)
- GET /api/v1/documents?case_id={id}&page=1&page_size=50
- GET /api/v1/tasks?case_id={id}&page=1&page_size=50
- GET /api/v1/fees/drafts?case_id={id}&page=1&page_size=50

## Constraints
- Use relative imports (e.g., ../../api/documents)
- Follow existing component patterns in frontend/src/modules/cases/components/
- Chinese text for headers and empty states
- No new API endpoints. Use existing filtered list endpoints
- No inline editing — tabs are read-only views with navigation buttons

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build

## Evidence
Write artifacts/FA1_plan/evidence.md with commands run and smoke test results.
```

---

## Batch FA2 — List UX Polish

**Goal**: Add missing filter controls to list pages and ensure consistent loading/empty states across all modules.

### Scope

| File | Change |
|------|--------|
| `frontend/src/modules/documents/pages/DocumentList.vue` | Add direction filter (IN/OUT/ALL dropdown) |
| `frontend/src/modules/tasks/pages/TaskList.vue` | Add status filter dropdown |
| `frontend/src/modules/billing/pages/BillList.vue` | Add status filter dropdown |
| `frontend/src/modules/fees/pages/FeeDraftList.vue` | Add status filter (OPEN/LOCKED) |

**Changes per page:**

1. **DocumentList** — Add `el-select` for direction filter (ALL / IN / OUT). Wire to existing `?direction=` query param.
2. **TaskList** — Add `el-select` for status filter (ALL / OPEN / IN_PROGRESS / COMPLETED / CANCELLED). Wire to existing `?status=` param.
3. **BillList** — Add `el-select` for status (ALL / ISSUED / PAID / VOID). Wire to existing `?status=` param.
4. **FeeDraftList** — Add `el-select` for status (ALL / OPEN / LOCKED). Wire to existing `?status=` param.

**Non-scope**: No new API parameters. Only wire existing filters to UI controls.

### Agent Team Prompt (FA2)

```
You are implementing Batch FA2 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
Several list pages lack filter dropdowns even though the backend APIs support filter parameters.

## Your Task
1. Read each list page to understand its current filter state
2. Add el-select filter controls above the table (in a filter bar row)
3. Wire each select to the corresponding API query parameter
4. Re-fetch list data when filter changes (watch + immediate fetch)

## File Allowlist
- frontend/src/modules/documents/pages/DocumentList.vue (modify)
- frontend/src/modules/tasks/pages/TaskList.vue (modify)
- frontend/src/modules/billing/pages/BillList.vue (modify)
- frontend/src/modules/fees/pages/FeeDraftList.vue (modify)

## Pattern
For each page, add above the el-table:
<el-row :gutter="16" style="margin-bottom: 16px">
  <el-col :span="6">
    <el-select v-model="filterX" placeholder="全部" clearable @change="fetchList">
      <el-option label="全部" value="" />
      <el-option label="X" value="X" />
    </el-select>
  </el-col>
</el-row>

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## ═══ PHASE A COMPLETE — No Backend Dependency ═══

After FA0–FA2, the frontend has:
- All case detail tabs showing real data
- Consistent filter controls on all list pages
- Verified baseline working state

**Proceed to Phase B only after backend batches A1–A5 are complete.**

---

## Batch FB1 — Task Detail Page + TaskLog View

**Goal**: Create the missing `/tasks/:id` detail page. Display task metadata, status actions, and audit log (from backend A1's `GET /tasks/{id}/logs` API).

**Requires**: Backend Batch A1 complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/api/tasks.ts` | Add `getTask(id)`, `getTaskLogs(taskId)` functions |
| `frontend/src/api/tasks.types.ts` | Add `TaskDetail`, `TaskLog` types |
| `frontend/src/modules/tasks/pages/TaskDetail.vue` | NEW: full detail page |
| `frontend/src/modules/tasks/components/TaskLogTimeline.vue` | NEW: audit log timeline |
| `frontend/src/router/index.ts` | Add route `/tasks/:id` |

**TaskDetail page layout:**

```
┌──────────────────────────────────────────┐
│ Header: Task Title          [Status Tag] │
│ Case: {case_no} (link)  Worker: {name}   │
├──────────────────────────────────────────┤
│ Tab: Overview │ Tab: Audit Log           │
├──────────────────────────────────────────┤
│ Overview:                                │
│   Due Date: 2026-03-15                   │
│   Internal Due: 2026-03-01               │
│   Base Date: 2026-01-15                  │
│   Supervisor: {name}                     │
│   Remark: {text}                         │
│   Created: 2026-01-16                    │
│                                          │
│ Actions: [Close] [Reopen] [Cancel]       │
├──────────────────────────────────────────┤
│ Audit Log tab:                           │
│   ● 2026-01-16 CREATED by admin          │
│   ● 2026-02-01 ASSIGNED to worker_a      │
│   ● 2026-02-15 COMPLETED by worker_a     │
└──────────────────────────────────────────┘
```

**Non-scope**: No task edit form. No reassign UI (SPEC 2.0 scope).

### Acceptance Criteria

- [ ] `/tasks/:id` route loads task detail with all metadata fields
- [ ] Status actions (Close/Reopen/Cancel) work with confirmation dialog
- [ ] Audit Log tab shows timeline from `GET /tasks/{id}/logs`
- [ ] Case link navigates to `/cases/{case_id}`
- [ ] Quality gate passes

### Agent Team Prompt (FB1)

```
You are implementing Batch FB1 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
FPMS frontend: Vue 3 + TypeScript + Element Plus.
The tasks module has TaskList and TaskCreate pages but NO TaskDetail page.
Backend A1 has been completed, adding:
- GET /api/v1/tasks/{id}/logs → returns list of TaskLog entries
- TaskLog fields: id, task_id, action, from_status, to_status, remark, created_at, created_by

## Your Task
1. Add API functions to frontend/src/api/tasks.ts:
   - getTask(id: string): GET /tasks/{id} (may already exist, verify)
   - getTaskLogs(taskId: string): GET /tasks/{taskId}/logs
2. Add types to frontend/src/api/tasks.types.ts:
   - TaskLog { id, task_id, action, from_status, to_status, remark, created_at, created_by }
3. Create frontend/src/modules/tasks/pages/TaskDetail.vue:
   - Fetch task on mount, display metadata in description list
   - Status actions: Close, Reopen, Cancel (using existing API: POST /tasks/{id}/close etc.)
   - Use el-tabs for Overview and Audit Log
4. Create frontend/src/modules/tasks/components/TaskLogTimeline.vue:
   - Fetch logs on mount, display as el-timeline
   - Each item: timestamp, action, from→to status, remark
5. Add route to frontend/src/router/index.ts:
   - { path: '/tasks/:id', component: TaskDetail, meta: { requiresAuth: true } }

## File Allowlist
- frontend/src/api/tasks.ts (modify)
- frontend/src/api/tasks.types.ts (modify)
- frontend/src/modules/tasks/pages/TaskDetail.vue (new)
- frontend/src/modules/tasks/components/TaskLogTimeline.vue (new)
- frontend/src/router/index.ts (modify)

## Constraints
- Follow CaseDetail.vue patterns for layout structure
- Use el-descriptions for metadata display
- Use el-timeline for audit log
- Chinese text for all labels
- Relative imports only

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## Batch FB2 — Client Detail + Address/Contact UI

**Goal**: Create client detail page. Add address and contact sub-resource management (CRUD) using backend A2's new APIs.

**Requires**: Backend Batch A2 complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/api/clients.ts` | Add address/contact CRUD functions |
| `frontend/src/api/clients.types.ts` | Add Address, Contact types |
| `frontend/src/modules/clients/pages/ClientDetail.vue` | NEW: tabbed detail page |
| `frontend/src/modules/clients/components/AddressTable.vue` | NEW: address CRUD table |
| `frontend/src/modules/clients/components/ContactTable.vue` | NEW: contact CRUD table |
| `frontend/src/router/index.ts` | Add route `/clients/:id` |

**ClientDetail layout:**

- Tab 1: **Basic Info** — client name, code, type, currency, email (read-only, edit button → ClientForm)
- Tab 2: **Addresses** — AddressTable with inline create/edit/delete
- Tab 3: **Contacts** — ContactTable with inline create/edit/delete
- Tab 4: **Related Cases** — filtered case list (GET /cases?client_id={id})

**Address fields**: address_type (BILLING/MAILING/GENERAL), address_line1, city, province, postal_code, country_code, is_default
**Contact fields**: contact_name, title, phone, mobile, email, is_primary

**Non-scope**: No client merge. No deduplication.

### Agent Team Prompt (FB2)

```
You are implementing Batch FB2 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
FPMS frontend: Vue 3 + TypeScript + Element Plus.
Backend A2 added sub-resource APIs for client addresses and contacts:
- GET/POST /clients/{id}/addresses
- PUT/DELETE /clients/{id}/addresses/{addr_id}
- GET/POST /clients/{id}/contacts
- PUT/DELETE /clients/{id}/contacts/{contact_id}

## Your Task
1. Add API functions to frontend/src/api/clients.ts:
   - listAddresses(clientId), createAddress(clientId, data), updateAddress(clientId, addrId, data), deleteAddress(clientId, addrId)
   - listContacts(clientId), createContact(clientId, data), updateContact(clientId, contactId, data), deleteContact(clientId, contactId)
2. Add types to frontend/src/api/clients.types.ts:
   - ClientAddress { id, client_id, address_type, address_line1, address_line2, city, province, postal_code, country_code, is_default }
   - ClientContact { id, client_id, contact_name, title, phone, mobile, email, is_primary }
3. Create ClientDetail.vue with el-tabs (Basic, Addresses, Contacts, Cases)
4. Create AddressTable.vue — el-table with el-dialog for add/edit, el-popconfirm for delete
5. Create ContactTable.vue — same pattern
6. Add route: /clients/:id → ClientDetail

## File Allowlist
- frontend/src/api/clients.ts (modify)
- frontend/src/api/clients.types.ts (modify)
- frontend/src/modules/clients/pages/ClientDetail.vue (new)
- frontend/src/modules/clients/components/AddressTable.vue (new)
- frontend/src/modules/clients/components/ContactTable.vue (new)
- frontend/src/router/index.ts (modify)

## Constraints
- address_type options: BILLING, MAILING, GENERAL (el-select)
- is_default / is_primary: el-switch in form, el-tag in table
- Delete requires el-popconfirm ("确定删除？")
- Follow existing ClientForm.vue patterns

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## Batch FB3 — Case Form Field Expansion

**Goal**: Add the 15 new case fields (from backend A3) to CaseCreate, CaseEdit, and CaseDetail pages. Organize in collapsible sections.

**Requires**: Backend Batch A3 complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/api/cases.types.ts` | Add 15 new fields to Case type |
| `frontend/src/modules/cases/pages/CaseCreate.vue` | Add optional field sections |
| `frontend/src/modules/cases/pages/CaseEdit.vue` | Add field sections |
| `frontend/src/modules/cases/pages/CaseDetail.vue` | Display new fields in Overview tab |

**New field groups (use el-collapse for organization):**

1. **Publication & Grant** (6 fields):
   `pub_date`, `pub_no`, `grant_date`, `grant_no`, `patent_no`, `valid_until`

2. **Specification** (3 fields):
   `spec_pages`, `claim_count`, `has_exam_request`

3. **Agent Assignment** (3 fields):
   `primary_agent_id`, `second_agent_id`, `draftor_id` — el-select loading users

4. **Control Flags** (3 fields):
   `is_fee_monitor`, `fee_reduction` (NONE/PARTIAL/FULL), `applicant_kind` (INDIVIDUAL/ENTITY/UNIV/GOV)

**Non-scope**: No conditional display per case_type (SPEC 2.0 scope). All fields shown for all types.

### Agent Team Prompt (FB3)

```
You are implementing Batch FB3 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
Backend A3 added 15 new columns to t_case. The case schemas now include:
pub_date, pub_no, grant_date, grant_no, patent_no, valid_until,
spec_pages, claim_count, has_exam_request,
primary_agent_id, second_agent_id, draftor_id,
is_fee_monitor, fee_reduction, applicant_kind

## Your Task
1. Update cases.types.ts — add all 15 fields (all optional/nullable)
2. Update CaseCreate.vue — add 4 collapsible sections (el-collapse) below existing fields:
   - "公告与授权" (Publication & Grant): date pickers + text inputs
   - "说明书信息" (Specification): number inputs + checkbox
   - "代理人分配" (Agent Assignment): user select dropdowns
   - "控制标记" (Control Flags): switch + select dropdowns
3. Update CaseEdit.vue — same 4 sections
4. Update CaseDetail.vue Overview tab — display new fields in el-descriptions

## File Allowlist
- frontend/src/api/cases.types.ts (modify)
- frontend/src/modules/cases/pages/CaseCreate.vue (modify)
- frontend/src/modules/cases/pages/CaseEdit.vue (modify)
- frontend/src/modules/cases/pages/CaseDetail.vue (modify)

## Constraints
- All 15 fields OPTIONAL in create/edit forms (el-form-item without required)
- Use el-collapse with default collapsed for new sections
- Date fields: el-date-picker with value-format="YYYY-MM-DD"
- Boolean fields: el-switch
- Enum fields: el-select with Chinese labels
- Agent ID fields: el-select loading from GET /api/v1/admin/users (if available) or text input fallback
- fee_reduction options: 不减免(NONE), 部分减免(PARTIAL), 全额减免(FULL)
- applicant_kind options: 个人(INDIVIDUAL), 企业(ENTITY), 高校(UNIV), 政府(GOV)

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## Batch FB4 — TaskTemplate Admin + SystemParam Enhancement

**Goal**: Create TaskTemplate management page. Verify SystemParam page works with new seeded params from backend A4.

**Requires**: Backend Batches A1 + A4 complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/api/tasks.ts` | Add TaskTemplate CRUD functions |
| `frontend/src/api/tasks.types.ts` | Add TaskTemplate types |
| `frontend/src/modules/system/pages/TaskTemplateList.vue` | NEW: template admin page |
| `frontend/src/router/index.ts` | Add route `/system/task-templates` |
| `frontend/src/constants/menu.ts` | Add "任务模板" menu item under 系统设置 |

**TaskTemplateList layout:**

- Table: code, name, add_days, add_months, inner_offset_days, default_worker_role, enabled (tag)
- Actions: Edit (dialog), Toggle enable/disable
- Create button → dialog form
- Dialog form fields: code, name, add_days (number), add_months (number), inner_offset_days (number), default_worker_role (text), description (textarea), enabled (switch)

**Non-scope**: No drag-and-drop ordering. No template preview/simulation.

### Agent Team Prompt (FB4)

```
You are implementing Batch FB4 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
Backend A1 added TaskTemplate CRUD APIs:
- GET /api/v1/task-templates → list all templates
- POST /api/v1/task-templates → create template
- PUT /api/v1/task-templates/{id} → update template
Backend A4 seeded default SystemParam values (case_no_prefix, default_currency, etc.)

## Your Task
1. Add API functions to tasks.ts: listTaskTemplates(), createTaskTemplate(data), updateTaskTemplate(id, data)
2. Add types: TaskTemplate { id, code, name, add_days, add_months, inner_offset_days, default_worker_role, enabled, description, created_at, updated_at }
3. Create TaskTemplateList.vue — el-table + el-dialog for create/edit
4. Add route /system/task-templates
5. Add menu item to constants/menu.ts under system settings group

## File Allowlist
- frontend/src/api/tasks.ts (modify)
- frontend/src/api/tasks.types.ts (modify)
- frontend/src/modules/system/pages/TaskTemplateList.vue (new)
- frontend/src/router/index.ts (modify)
- frontend/src/constants/menu.ts (modify)

## Constraints
- code field: read-only in edit mode (prevent changing code after creation)
- add_days/add_months/inner_offset_days: el-input-number, min=0
- enabled: el-switch, display as el-tag (success/info) in table
- Follow SystemParams.vue patterns for inline table + dialog

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## Batch FB5 — Case Advanced Search Filter Panel

**Goal**: Add a filter panel to CaseList with 8 filter parameters from backend A5.

**Requires**: Backend Batch A5 complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/api/cases.ts` | Add filter params to listCases() |
| `frontend/src/modules/cases/pages/CaseList.vue` | Add filter panel |

**Filter panel (collapsible el-card above table):**

| Filter | UI Control | API Param |
|--------|-----------|-----------|
| 客户 (Client) | el-select (load from GET /clients) | client_id |
| 案件类型 (Case Type) | el-select (NORMAL, etc.) | case_type |
| 专利类别 (Patent Category) | el-select (INV, UTL, DES) | patent_category |
| 流向 (Flow Dir) | el-select (CN_DOMESTIC, etc.) | flow_dir |
| 状态 (Status) | el-select (all CaseStatus values) | status |
| 申请日从 (Filing From) | el-date-picker | filing_date_from |
| 申请日至 (Filing To) | el-date-picker | filing_date_to |
| 主办代理人 (Agent) | el-select (users, if available) | primary_agent_id |

**Layout**: Use `el-row`/`el-col` grid, 4 filters per row. "搜索" button + "重置" button.

**Non-scope**: No saved searches. No URL query persistence (keep it simple for MVP1).

### Agent Team Prompt (FB5)

```
You are implementing Batch FB5 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
Backend A5 extended GET /api/v1/cases to accept:
client_id, case_type, patent_category, flow_dir, status, filing_date_from, filing_date_to, primary_agent_id

## Your Task
1. Update cases.ts listCases() to accept and pass filter params
2. Update CaseList.vue:
   - Add collapsible filter panel (el-card with el-collapse-transition)
   - 8 filter controls in 2-row grid layout
   - "搜索" and "重置" buttons
   - On search: re-fetch with all filter params, reset page to 1
   - On reset: clear all filters, re-fetch
3. Client selector: load top 100 clients from GET /api/v1/clients for el-select options

## File Allowlist
- frontend/src/api/cases.ts (modify)
- frontend/src/modules/cases/pages/CaseList.vue (modify)

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## ═══ FE MVP1 SCOPE GATE ═══

After FB5, verify frontend covers all MVP1 success criteria:

```
✅ Case CRUD with 15 SPEC fields + advanced search
✅ Document creation + case detail docs tab
✅ Task creation + detail page with audit log
✅ Fee draft → Bill → Payment flow with UI
✅ Client with addresses & contacts
✅ TaskTemplate admin + SystemParam management
✅ All list pages have consistent filters
```

If all pass, proceed to Phase C. If any fail, fix before continuing.

---

## Batch FC1 — DocTemplate Admin UI

**Goal**: Create DocTemplate management page for the configuration-driven document automation system from backend B1.

**Requires**: Backend Batch B1 complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/api/documents.ts` | Add DocTemplate CRUD functions |
| `frontend/src/api/documents.types.ts` | Add DocTemplate types |
| `frontend/src/modules/system/pages/DocTemplateList.vue` | NEW: template admin page |
| `frontend/src/router/index.ts` | Add route `/system/doc-templates` |
| `frontend/src/constants/menu.ts` | Add "文件模板" menu item |

**DocTemplateList layout:**

- Table: code, name, direction, status_effect, deadline_template_code, fee_draft_type, need_reply, enabled
- Create/Edit dialog with fields:
  - code (required), name (required), direction (IN/OUT), enabled (switch)
  - status_effect (text — case status to set)
  - deadline_template_code (el-select from TaskTemplates)
  - fee_draft_type (text)
  - need_reply (switch)
  - reply_to_template_code (text)
  - fee_item_list (textarea, JSON — with placeholder example)
  - input_fields (textarea, JSON)

**Non-scope**: No visual JSON editor. No cascade preview. Configuration only — the cascade logic is backend-side.

### Agent Team Prompt (FC1)

```
You are implementing Batch FC1 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
Backend B1 added DocTemplate CRUD:
- GET /api/v1/doc-templates
- POST /api/v1/doc-templates
- PUT /api/v1/doc-templates/{id}
- GET /api/v1/doc-templates/{id}

DocTemplate fields: id, code, name, direction, enabled, status_effect, status_restore,
deadline_template_code, fee_draft_type, fee_item_list, need_reply, reply_to_template_code, input_fields

## Your Task
1. Add API functions to documents.ts
2. Add DocTemplate type to documents.types.ts
3. Create DocTemplateList.vue — table + create/edit dialog
4. Add route /system/doc-templates
5. Add "文件模板" to menu.ts under system settings

## File Allowlist
- frontend/src/api/documents.ts (modify)
- frontend/src/api/documents.types.ts (modify)
- frontend/src/modules/system/pages/DocTemplateList.vue (new)
- frontend/src/router/index.ts (modify)
- frontend/src/constants/menu.ts (modify)

## Constraints
- fee_item_list: textarea with JSON placeholder: [{"fee_code":"REG_FEE","fee_name":"登记费","amount":200}]
- deadline_template_code: el-select populated from GET /api/v1/task-templates
- Follow TaskTemplateList.vue pattern from FB4

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## Batch FC2 — Document Reply Chain + Template Selection

**Goal**: Add template selection to DocumentCreate. Display reply chain info in DocumentDetail. Show need_reply indicator in DocumentList.

**Requires**: Backend Batch B2 complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/api/documents.types.ts` | Add reply_to_id, need_reply, reply_date, doc_template_id fields |
| `frontend/src/modules/documents/pages/DocumentCreate.vue` | Add template selector + reply_to field |
| `frontend/src/modules/documents/pages/DocumentDetail.vue` | Show reply chain info |
| `frontend/src/modules/documents/pages/DocumentList.vue` | Add need_reply indicator column |

**DocumentCreate enhancements:**
- Add `doc_template_id` el-select (load from GET /doc-templates, show code + name)
- Add `reply_to_id` el-select (load documents for same case, show title + direction)
- When template selected with need_reply=true, show info tag "需要回复"
- On template select, auto-set direction from template.direction

**DocumentDetail enhancements:**
- If document.need_reply=true, show "待回复" warning tag
- If document.reply_date is set, show "已于 {date} 回复" success tag
- If document.reply_to_id is set, show link to original document

**DocumentList enhancement:**
- Add "需回复" column with el-tag (warning) when need_reply=true and reply_date is null

**Non-scope**: No document wizard (5-step). That's SPEC 2.0 stretch scope. Interface stub only via template selection.

### Agent Team Prompt (FC2)

```
You are implementing Batch FC2 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
Backend B2 added reply chain fields to Document:
- reply_to_id: String (FK to another document)
- need_reply: Boolean
- reply_date: Date (set when reply registered)

DocTemplate (from B1) has: need_reply, status_effect, deadline_template_code.
When creating a document with a template, the backend auto-applies status changes and task generation.

## Your Task
1. Update documents.types.ts with new fields
2. Update DocumentCreate.vue:
   - Add doc_template_id el-select (fetch from GET /doc-templates, filter by direction)
   - Add reply_to_id el-select (fetch docs for same case_id)
   - On template select: auto-set direction, show need_reply indicator
3. Update DocumentDetail.vue:
   - Display reply chain: "回复文件: {original_doc.title}" (link)
   - Display need_reply/reply_date status
4. Update DocumentList.vue:
   - Add "待回复" column with conditional el-tag

## File Allowlist
- frontend/src/api/documents.types.ts (modify)
- frontend/src/modules/documents/pages/DocumentCreate.vue (modify)
- frontend/src/modules/documents/pages/DocumentDetail.vue (modify)
- frontend/src/modules/documents/pages/DocumentList.vue (modify)

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## Batch FC3 — Fee Rate Dimensions Display

**Goal**: Display the new fee rate dimension columns (from backend B4) in the FeeRates page. Update FeeRateForm.

**Requires**: Backend Batch B4 complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/api/fees.types.ts` | Add dimension fields to FeeRate type |
| `frontend/src/modules/fees/pages/FeeRates.vue` | Add columns to table |
| `frontend/src/modules/fees/components/FeeRateForm.vue` | Add dimension fields to form |

**New fields to display:**
- rate_group (DOMESTIC/PCT/ANNUITY)
- country_code
- case_type, patent_category
- calc_mode (FIXED/PER_CLAIM/PER_PAGE/TIER — read-only display)
- allow_reduction (boolean)
- effective_from, effective_to (dates)

**Non-scope**: No fee calculation UI. No TIER rule editor. Display and simple create/edit only.

### Agent Team Prompt (FC3)

```
You are implementing Batch FC3 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
Backend B4 added 9 dimension columns to t_fee_rate:
rate_group, country_code, case_type, patent_category, calc_mode, calc_params,
allow_reduction, effective_from, effective_to.

## Your Task
1. Update fees.types.ts with new FeeRate fields
2. Update FeeRates.vue table: add columns for rate_group, calc_mode, effective dates
3. Update FeeRateForm.vue: add form fields for new dimensions
   - rate_group: el-select (DOMESTIC/PCT/ANNUITY)
   - calc_mode: el-select (FIXED/PER_CLAIM/PER_PAGE/TIER) — default FIXED
   - effective_from/to: el-date-picker
   - allow_reduction: el-switch
   - country_code, case_type, patent_category: el-select or text input

## File Allowlist
- frontend/src/api/fees.types.ts (modify)
- frontend/src/modules/fees/pages/FeeRates.vue (modify)
- frontend/src/modules/fees/components/FeeRateForm.vue (modify)

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## Batch FC4 — Billing Offset Reversal + Receipt Enrichment

**Goal**: Add offset reversal button. Display enriched CaseReceipt fields from backend B5.

**Requires**: Backend Batch B5 complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/api/billing.ts` | Add reverseOffset() function |
| `frontend/src/api/billing.types.ts` | Add is_reversed field, enrich CaseReceipt |
| `frontend/src/modules/billing/pages/BillDetail.vue` | Add reverse button on offsets |
| `frontend/src/modules/cases/components/CaseReceiptsSummary.vue` | Display enriched receipt fields |

**BillDetail enhancements:**
- In offsets section: if offset.is_reversed=false, show "撤销" (Reverse) button
- On click: el-popconfirm "确定撤销此抵扣？" → POST /offsets/{id}/reverse
- If offset.is_reversed=true, show "已撤销" (Reversed) danger tag

**CaseReceipt enhancements:**
- Display fee_code, year_no, is_arrears columns in receipt table
- is_arrears: show "欠费" danger tag

**Non-scope**: No prepayment management. No dunning UI.

### Agent Team Prompt (FC4)

```
You are implementing Batch FC4 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
Backend B5 added:
- POST /api/v1/offsets/{offset_id}/reverse — reverses an offset
- CaseReceipt now includes: fee_code, year_no, is_arrears, invoice_no, is_commissionable

## Your Task
1. Add reverseOffset(offsetId) to billing.ts
2. Update billing.types.ts: add is_reversed, reversed_at to Offset; add new CaseReceipt fields
3. Update BillDetail.vue: add reverse button with confirmation on each offset row
4. Update CaseReceiptsSummary.vue: display fee_code, year_no, is_arrears columns

## File Allowlist
- frontend/src/api/billing.ts (modify)
- frontend/src/api/billing.types.ts (modify)
- frontend/src/modules/billing/pages/BillDetail.vue (modify)
- frontend/src/modules/cases/components/CaseReceiptsSummary.vue (modify)

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## Batch FC5 — Cross-entity List Enrichment

**Goal**: Display `client_name` and `case_no` in task and document lists using the enriched responses from backend B6.

**Requires**: Backend Batch B6 complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/api/tasks.types.ts` | Add client_name to Task type |
| `frontend/src/api/documents.types.ts` | Ensure case_no in Document type |
| `frontend/src/modules/tasks/pages/TaskList.vue` | Add client_name column |
| `frontend/src/modules/documents/pages/DocumentList.vue` | Add case_no column (if missing) |
| `frontend/src/modules/tasks/pages/TaskList.vue` | Add client_id filter |
| `frontend/src/modules/documents/pages/DocumentList.vue` | Add client_id filter |

**Changes:**
- TaskList: Add "客户" column showing client_name. Add client_id filter (el-select).
- DocumentList: Add "案件号" column showing case_no (if not already). Add client_id filter.

**Non-scope**: No full-text search. No Elasticsearch.

### Agent Team Prompt (FC5)

```
You are implementing Batch FC5 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
Backend B6 enriched list responses:
- GET /tasks now includes client_name in each item
- GET /documents now includes case_no in each item
- Both endpoints accept client_id filter parameter

## Your Task
1. Update task types to include client_name
2. Update document types to include case_no
3. Add client_name column to TaskList table
4. Ensure case_no column exists in DocumentList table
5. Add client_id filter (el-select, load from GET /clients) to both lists

## File Allowlist
- frontend/src/api/tasks.types.ts (modify)
- frontend/src/api/documents.types.ts (modify)
- frontend/src/modules/tasks/pages/TaskList.vue (modify)
- frontend/src/modules/documents/pages/DocumentList.vue (modify)

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## Batch FC6 — Dashboard Polish + Final Verification

**Goal**: Fix dashboard KPI fragility (client-side aggregation with page_size=200). Add final UI polish. Run comprehensive E2E smoke test.

**Requires**: All previous FE + BE batches complete.

### Scope

| File | Change |
|------|--------|
| `frontend/src/modules/dashboard/dashboard.api.ts` | Improve KPI fetching strategy |
| `frontend/src/modules/dashboard/pages/Dashboard.vue` | Polish KPI display |
| `frontend/src/modules/dashboard/components/ActionCenter.vue` | Show client_name in tasks |

**KPI improvements:**
- Increase page_size for KPI aggregation queries to handle larger datasets (or use total from pagination response)
- Fix unallocated payments: only count payments without full offset (check balance field)
- Use `total` field from paginated responses instead of counting items

**ActionCenter improvements:**
- Show client_name alongside case_no in task rows (available after B6)

**Final E2E verification:**
```bash
# Full smoke: login → dashboard → navigate all modules → verify no console errors
# Verify all new pages: /tasks/:id, /clients/:id, /system/task-templates, /system/doc-templates
# Verify all case detail tabs show data
# Verify filters work on all list pages
```

**Non-scope**: No dedicated `/api/v1/dashboard/kpi` endpoint (would require backend change).

### Agent Team Prompt (FC6)

```
You are implementing Batch FC6 of the FPMS MVP1 Frontend Enhancement Plan.

## Context
This is the final FE batch. All backend batches A0–B6 and frontend batches FA0–FC5 are complete.

## Your Task
1. Improve dashboard.api.ts:
   - Use response.total instead of items.length for KPI counts
   - Fix unallocated payments metric to check payment balance
2. Update ActionCenter.vue to display client_name (now available in task responses)
3. Run comprehensive quality gate + manual smoke test
4. Document results in artifacts/FC6_plan/summary.md

## File Allowlist
- frontend/src/modules/dashboard/dashboard.api.ts (modify)
- frontend/src/modules/dashboard/pages/Dashboard.vue (modify)
- frontend/src/modules/dashboard/components/ActionCenter.vue (modify)

## Quality Gate (MUST pass)
cd frontend && npm run lint && npm run typecheck && npm run build

## Final E2E Smoke Test
- Login as admin → Dashboard loads with KPI cards
- Cases: list → create → detail (all 4 tabs have data) → edit (15 fields) → search (8 filters)
- Tasks: list → create → detail (with audit log) → close/reopen
- Documents: list → create (with template selection) → detail (reply chain)
- Fees: rates → drafts → items → lock
- Billing: bills → payments → offsets → reverse offset
- Clients: list → create → detail (addresses, contacts tabs)
- System: params, task templates, doc templates
```

---

## ═══ FE SPEC ALIGNMENT GATE ═══

After FC6, verify the complete frontend chain:

```
✅ Case CRUD with 15+ SPEC fields + 8 search filters + 4 detail tabs
✅ Document create with template selection + reply chain display
✅ Task detail with audit log + TaskTemplate admin
✅ Client detail with address/contact CRUD
✅ Fee rates with dimensions + Billing with offset reversal
✅ DocTemplate config admin (automation cascade driven by backend)
✅ Dashboard with reliable KPIs + cross-entity enrichment
✅ All lists with consistent filters + loading/empty states
```

---

## 3. Batch Execution Summary

| Batch | Name | Priority | Depends On | Est. Files | Key Deliverable |
|-------|------|----------|------------|------------|-----------------|
| **FA0** | FE Baseline Smoke | P0 | — | 0 | Verified FE working state |
| **FA1** | Case Detail Tabs | P0 | FA0 | 5 | 4 stubbed tabs replaced with data |
| **FA2** | List UX Polish | P1 | FA1 | 4 | Consistent filters on all lists |
| | **═══ PHASE A ═══** | | FA2 | | Independent FE fixes done |
| **FB1** | TaskDetail + TaskLog | P0 | FA2 + BE A1 | 5 | Missing detail page created |
| **FB2** | ClientDetail + Addr/Contact | P0 | FB1 + BE A2 | 6 | Client sub-resource UI |
| **FB3** | Case Field Expansion | P1 | FB2 + BE A3 | 4 | 15 new fields in forms |
| **FB4** | TaskTemplate + SysParam Admin | P1 | FB3 + BE A1/A4 | 5 | Template config page |
| **FB5** | Case Advanced Search | P1 | FB4 + BE A5 | 2 | 8-filter search panel |
| | **═══ FE MVP1 GATE ═══** | | FB5 | | MVP1 scope fully covered |
| **FC1** | DocTemplate Admin | P1 | FB5 + BE B1 | 5 | Doc automation config page |
| **FC2** | Doc Reply Chain + Template | P1 | FC1 + BE B2 | 4 | OA lifecycle FE support |
| **FC3** | FeeRate Dimensions | P2 | FC2 + BE B4 | 3 | Multi-dim rate display |
| **FC4** | Offset Reversal + Receipts | P2 | FC3 + BE B5 | 4 | Billing polish |
| **FC5** | List Enrichment | P2 | FC4 + BE B6 | 4 | Cross-entity search |
| **FC6** | Dashboard Polish + E2E | P2 | FC5 | 3 | Final quality pass |
| | **═══ FE SPEC GATE ═══** | | FC6 | | Full SPEC alignment |

**Total batches**: 15 (+ 2 gates)
**Total estimated files changed/created**: ~54

---

## 4. How to Execute: Agent Team Launch Protocol

### For each batch, use this pattern:

```
1. Verify prerequisite backend batch is complete (if any)
2. Launch Claude Code agent team with the prompt from the corresponding batch section
3. Agent executes within File Allowlist only
4. Agent runs quality gate
5. Agent writes evidence log to artifacts/{BATCH}_plan/evidence.md
6. Human reviews diff + evidence
7. Commit: git commit -m "feat(FE): Batch {ID} — {name}"
8. Proceed to next batch
```

### Recommended team approach per batch:

| Batch | Approach | Why |
|-------|----------|-----|
| FA0 | Single agent | Verification only |
| FA1 | Single agent | 4 components + 1 page modify |
| FA2 | Single agent | 4 page modifications |
| FB1 | Single agent | New page + component + API |
| FB2 | 2-agent team (API+UI / Test) | Most complex: 3 new components + API |
| FB3 | Single agent | Form field additions |
| FB4 | Single agent | New page + API |
| FB5 | Single agent | Filter panel additions |
| FC1 | Single agent | New page (follows FB4 pattern) |
| FC2 | Single agent | 4 page modifications |
| FC3 | Single agent | 3 file modifications |
| FC4 | Single agent | 4 file modifications |
| FC5 | Single agent | 4 file modifications |
| FC6 | Single agent | Polish + E2E test |

### Post-batch checklist:

```
□ Quality gate passes (npm run lint && npm run typecheck && npm run build)
□ Manual smoke test of affected pages (no console errors)
□ Evidence log written to artifacts/{BATCH}_plan/
□ Batch diff reviewed (no files outside allowlist modified)
□ Git commit: "feat(FE): Batch {ID} — {name}"
```

### STOP Contract (applies to ALL batches):

```
STOP and create a new atomic fix task if:
- Any file outside the allowlist needs modification
- A backend API returns unexpected schema (mismatch with documented contract)
- An Element Plus component doesn't support the required interaction pattern
- npm run build fails and the fix requires changes outside allowlist
- A CORS or auth issue blocks API calls
```

---

## 5. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Backend batch not complete when FE batch starts | Medium | High | Dependency matrix enforced; FE Phase A has zero BE dependency |
| API response schema mismatch | Low | Medium | Each agent prompt specifies exact expected fields; STOP on mismatch |
| Element Plus breaking change | Low | Low | Pin version in package.json; no upgrades during enhancement |
| CSS variable conflicts with demo-mode | Medium | Low | Test with both VITE_DEMO_UI=0 and =1 in smoke tests |
| New pages not added to sidebar menu | Low | Medium | Each batch prompt explicitly includes menu.ts in allowlist when needed |
| TypeScript type mismatches with backend | Medium | Medium | types.ts files updated FIRST in each batch; all fields optional/nullable |

---

## 6. Document Generation — Interface Stub Strategy

Per user requirement, document generation features (Word template rendering, batch document wizard) are **interface-only** since concrete templates are not available:

| Feature | Current State | This Plan's Approach |
|---------|--------------|---------------------|
| Bill print (docx) | Working (BillDetail has print button) | No change needed |
| Document template selection | Not implemented | FC2: Add el-select in DocumentCreate (template selection triggers backend cascade) |
| Document wizard (5-step) | Not implemented | **NOT in scope** — frozen feature (template builder UI) |
| Task sheet print | Backend supports | **NOT in scope** — requires template file |
| Envelope/dispatch print | Not implemented | **NOT in scope** — frozen feature |

The DocTemplate admin (FC1) allows administrators to **configure** templates that drive backend automation. The actual document **rendering** requires Word template files (`.docx`) which are out of MVP1 scope.
