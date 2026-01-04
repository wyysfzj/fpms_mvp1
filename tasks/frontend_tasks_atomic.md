# Frontend Atomic Tasks (MVP1) — 1 file per task
> DB prerequisite: see `backend/docs/db_migrations_overview.md`  
> Run `cd backend && alembic upgrade head` before backend tasks.

> Target stack: **Vue 3 + TypeScript + Pinia + Element Plus + Vite** under `frontend/`.
>
> Atomic rule (to reduce Copilot drift):
> - Each task MUST change **only the listed file** (or create exactly **one** new file).
> - Each task MUST implement **only the named component / store / API client module**.
> - Follow design contracts in:
>   - `docs/01_information_architecture.md`
>   - `docs/02_permissions_rbac.md`
>   - `frontend/src/modules/**/docs/*`

---

## FE-00 Bootstrap & Auth

### FE-00-01 — Improve API client error handling
**File:** `frontend/src/api/http.ts`

**Prompt**
Update `src/api/http.ts` ONLY:
- Add a response interceptor:
  - if status is 401 -> remove `fpms_token` and redirect to `/login` (use `window.location.href` to avoid router import cycles)
  - if response body is `{error:{code,message,details}}` keep it as-is (do not wrap)
- Export a helper `getApiErrorMessage(e:any): string` that extracts `error.message` when present.
Constraints:
- Do not add other files.

### FE-00-02 — Create Auth types
**File:** `frontend/src/types/auth.ts` (new)

**Prompt**
Create `src/types/auth.ts` defining ONLY TypeScript types:
- `export type PermCode = string`
- `export interface UserMe { id: string; username: string; display_name?: string; roles: string[]; permissions: PermCode[] }`
- `export interface TokenResponse { access_token: string; token_type?: string }`
Constraints:
- No API calls in this file.

### FE-00-03 — Create Auth Pinia store
**File:** `frontend/src/store/auth.ts` (new)

**Prompt**
Create `src/store/auth.ts` implementing ONLY `useAuthStore` (Pinia):
- state: `token: string | null`, `me: UserMe | null`, `loadingMe: boolean`
- getters:
  - `isLoggedIn`
  - `hasPerm(code: string): boolean`
- actions:
  - `setToken(token: string | null)` (also sync localStorage key `fpms_token`)
  - `fetchMe()` calls `GET /auth/me` and stores into `me`
  - `logout()` clears token and me
Notes:
- use `http` from `src/api/http.ts`
- use types from `src/types/auth.ts`
Constraints:
- Do not change any other files.

### FE-00-04 — Wire login page to Auth store
**File:** `frontend/src/modules/auth/pages/Login.vue`

**Prompt**
Update `Login.vue` ONLY:
- Use `useAuthStore`.
- On login success:
  - `auth.setToken(data.access_token)`
  - `await auth.fetchMe()`
  - redirect to `/dashboard`
- On error show `ElMessage.error(getApiErrorMessage(e))`
Constraints:
- Do not modify router or layout in this task.

### FE-00-05 (docs/01_information_architecture.md) — Add route meta for permissions
**File:** `frontend/src/router/index.ts`

**Prompt**
Update `router/index.ts` ONLY:
- Add `meta` to each protected route with:
  - `requiresAuth: true`
  - `perm?: string` (single perm code) or `perms?: string[]` (any-of)
- Use permission codes from `docs/02_permissions_rbac.md`.
- For now assign:
  - dashboard: `requiresAuth` only
  - cases list: `Case.Read`
  - case detail: `Case.Read`
  - documents: `Doc.Read`
  - tasks: `Task.Read`
  - fees drafts: `Fee.Read`
  - billing bills: `Bill.Read`
  - settings clients: `Client.Manage`
Constraints:
- Do not implement guards yet.

### FE-00-06 — Implement auth + permission route guard
**File:** `frontend/src/router/index.ts`

**Prompt**
In `router/index.ts`, implement ONLY a `beforeEach` guard:
- If route has `meta.requiresAuth` and no token -> redirect to `/login`.
- If token exists but `auth.me` is null -> call `await auth.fetchMe()`.
- If route has `meta.perm` -> require `auth.hasPerm(perm)`.
- If route has `meta.perms` -> require ANY of them.
- If permission check fails -> redirect to `/dashboard`.
Constraints:
- Keep existing routes.
- Only change `router/index.ts`.

### FE-00-07 (docs/01_information_architecture.md) — Build dynamic left menu
**File:** `frontend/src/layout/MainLayout.vue`

**Prompt**
Update `MainLayout.vue` ONLY:
- Replace hard-coded links with an Element Plus menu (`el-menu` + `el-menu-item`).
- Menu items should be generated from a local array describing:
  - label, path, required perm (optional)
- Filter items by `auth.hasPerm` when perm exists.
- Add a top bar area showing current username and a Logout button.
- On logout: `auth.logout()` and navigate to `/login`.
Constraints:
- Do not create new components; keep all in this file.

---

## FE-01 Cases (frontend/src/modules/cases/docs/case_00_overview.md)

### FE-01-01 — Create Cases API client
**File:** `frontend/src/modules/cases/api.ts` (new)

**Prompt**
Create `modules/cases/api.ts` with ONLY exported functions calling backend:
- `listCases(params)` -> GET `/cases`
- `getCase(id)` -> GET `/cases/${id}`
- `createCase(payload)` -> POST `/cases`
- `updateCase(id,payload)` -> PUT `/cases/${id}`
- `limitedEditCase(id,payload)` -> POST `/cases/${id}/limited-edit`
- `exportCases(params)` -> GET `/cases/export` (responseType: 'blob')
Use `http` from `src/api/http.ts`.
Constraints:
- Do not create store or UI.

### FE-01-02 — Create Cases Pinia store
**File:** `frontend/src/modules/cases/store.ts` (new)

**Prompt**
Create `modules/cases/store.ts` implementing ONLY `useCasesStore`:
- state: list filters, pagination, `items`, `total`, `currentCase`.
- actions:
  - `fetchList()` calls `listCases`
  - `fetchDetail(id)` calls `getCase`
Constraints:
- Do not implement UI.

### FE-01-03 — Implement CaseList page (search/list/export)
**File:** `frontend/src/modules/cases/pages/CaseList.vue`

**Prompt**
Implement `CaseList.vue` ONLY:
- Use Element Plus form + table.
- Filters per IA and backend `case_02_api.md`:
  - q, case_no, app_no, client_id(optional), status(optional), date_from/date_to(optional)
- Table columns: CaseNo, Title_CN, Client, Status, FilingDate(optional), UpdatedAt.
- Pagination + sorting (sort_by, sort_dir).
- Row click -> route to `/cases/:id`.
- Export button -> call `exportCases` and download CSV.
Constraints:
- Do not implement create case in this task.

### FE-01-04 — Implement CaseDetail shell with tabs
**File:** `frontend/src/modules/cases/pages/CaseDetail.vue`

**Prompt**
Implement `CaseDetail.vue` ONLY:
- On mounted, read route param `id` and call `cases.fetchDetail(id)`.
- Render `el-tabs`:
  - Overview
  - Parties
  - Documents
  - Tasks
  - Fees
  - Billing
- For MVP1, tab contents can be simple placeholders showing JSON blocks of current case.
- Show a button "Limited Edit" only if `auth.hasPerm('Case.EditLimited')`.
Constraints:
- Do not create new component files.

---

## FE-02 Documents (frontend/src/modules/documents/docs/doc_00_overview.md)

### FE-02-01 — Create Documents API client
**File:** `frontend/src/modules/documents/api.ts` (new)

**Prompt**
Create `modules/documents/api.ts` exporting ONLY:
- `listDocuments(params)` -> GET `/documents`
- `createDocument(payload)` -> POST `/documents`
- `getDocument(id)` -> GET `/documents/${id}`
- `updateDocument(id,payload)` -> PUT `/documents/${id}`
- `uploadAttachment(id,file)` -> POST `/documents/${id}/attachments` (multipart)
- `downloadAttachment(id,attId)` -> GET `/documents/${id}/attachments/${attId}/download` (blob)
Constraints:
- Use `http`.

### FE-02-02 — Implement Document list/register UI
**File:** `frontend/src/modules/documents/pages/DocumentList.vue`

**Prompt**
Implement `DocumentList.vue` ONLY:
- Filters: direction(IN/OUT), q, doc_template_id(optional), case_id(optional), date_from/date_to.
- Table columns: DocDate, Direction, Title, RefNo, CaseNo(optional).
- Provide a "Register" drawer or dialog form:
  - fields: case_id, doc_template_id, direction, doc_date, title, ref_no
  - after create, allow uploading 1+ attachments.
Constraints:
- Keep everything in this single page for MVP1.

---

## FE-03 Tasks / Docket (frontend/src/modules/tasks/docs/task_00_overview.md)

### FE-03-01 — Create Tasks API client
**File:** `frontend/src/modules/tasks/api.ts` (new)

**Prompt**
Create `modules/tasks/api.ts` exporting ONLY:
- `listTasks(params)` -> GET `/tasks`
- `createTask(payload)` -> POST `/tasks`
- `getTask(id)` -> GET `/tasks/${id}`
- `updateTask(id,payload)` -> PUT `/tasks/${id}`
- `closeTask(id, payload?)` -> POST `/tasks/${id}/close`
- `reopenTask(id, payload?)` -> POST `/tasks/${id}/reopen`
- `cancelTask(id, payload?)` -> POST `/tasks/${id}/cancel`
- `todayTasks(as)` -> GET `/tasks/today?as=${as}`
Constraints:
- Use `http`.

### FE-03-02 — Implement Task list + today reminders page
**File:** `frontend/src/modules/tasks/pages/TaskList.vue`

**Prompt**
Implement `TaskList.vue` ONLY:
- Two tabs:
  1) "All Tasks" -> list with filters: status, due date range, worker, supervisor, case
  2) "Today" -> call `todayTasks(as)` with selector worker|supervisor
- Provide inline actions: Close/Reopen/Cancel (buttons shown only when user has related perms).
Constraints:
- No separate task detail page in MVP1.

---

## FE-04 Fees (frontend/src/modules/fees/docs/fee_00_overview.md)

### FE-04-01 — Create Fees API client
**File:** `frontend/src/modules/fees/api.ts` (new)

**Prompt**
Create `modules/fees/api.ts` exporting ONLY:
- draft:
  - `listDrafts(params)` GET `/fees/drafts`
  - `createDraft(payload)` POST `/fees/drafts`
  - `getDraft(id)` GET `/fees/drafts/${id}`
  - `updateDraft(id,payload)` PUT `/fees/drafts/${id}`
  - `lockDraft(id)` POST `/fees/drafts/${id}/lock`
  - `unlockDraft(id)` POST `/fees/drafts/${id}/unlock`
- items:
  - `addItem(draftId,payload)` POST `/fees/drafts/${draftId}/items`
  - `updateItem(itemId,payload)` PUT `/fees/items/${itemId}`
  - `deleteItem(itemId)` DELETE `/fees/items/${itemId}`
- rates:
  - `listRates(params)` GET `/fees/rates`
  - `createRate(payload)` POST `/fees/rates`
  - `updateRate(id,payload)` PUT `/fees/rates/${id}`
Constraints:
- Use `http`.

### FE-04-02 — Implement Fee drafts list + draft editor
**File:** `frontend/src/modules/fees/pages/FeeDraftList.vue`

**Prompt**
Implement `FeeDraftList.vue` ONLY:
- Left: Draft list (filters by case/client/status).
- Right: Draft detail editor when selected:
  - header fields (currency, status)
  - items table editable: FeeCode/FeeName/FeeType/YearNo/Quantity/UnitPrice/Amount/Remark
  - buttons: Add item, Save, Lock/Unlock
- If draft is LOCKED: disable editing.
Constraints:
- No separate route; keep single page.

---

## FE-05 Billing (frontend/src/modules/billing/docs/bill_00_overview.md)

### FE-05-01 — Create Billing API client
**File:** `frontend/src/modules/billing/api.ts` (new)

**Prompt**
Create `modules/billing/api.ts` exporting ONLY:
- bills:
  - `listBills(params)` GET `/billing/bills`
  - `getBill(id)` GET `/billing/bills/${id}`
  - `createBillFromDrafts(payload)` POST `/billing/bills/from-drafts`
  - `printBill(id)` GET `/billing/bills/${id}/print` (blob)
- payments:
  - `listPayments(params)` GET `/billing/payments`
  - `createPayment(payload)` POST `/billing/payments`
  - `getPayment(id)` GET `/billing/payments/${id}`
- offsets:
  - `createOffset(payload)` POST `/billing/offsets`
- receipts:
  - `getCaseReceipts(caseId)` GET `/billing/cases/${caseId}/receipts`
Constraints:
- Use `http`.

### FE-05-02 — Implement Bill list UI
**File:** `frontend/src/modules/billing/pages/BillList.vue`

**Prompt**
Implement `BillList.vue` ONLY:
- Table with filters: client, status, bill date range.
- Row expand or drawer to show bill detail and items.
- Button "Print" downloads docx via `printBill`.
Constraints:
- Keep offsets and payments as future in this page; only show placeholders/links.

---

## FE-06 Settings (frontend/src/modules/settings/docs/settings_00_overview.md)

### FE-06-01 — Create Clients API client (settings)
**File:** `frontend/src/modules/settings/api.ts` (new)

**Prompt**
Create `modules/settings/api.ts` exporting ONLY:
- `listClients(params)` GET `/clients`
- `createClient(payload)` POST `/clients`
- `updateClient(id,payload)` PUT `/clients/${id}`
- `deactivateClient(id)` PUT `/clients/${id}/deactivate`
Constraints:
- Use `http`.

### FE-06-02 — Implement Client maintenance page
**File:** `frontend/src/modules/settings/pages/ClientList.vue`

**Prompt**
Implement `ClientList.vue` ONLY:
- List clients with search by code/name.
- Drawer form for create/edit.
- Nested tables for addresses and contacts (editable in drawer).
- Deactivate action.
Constraints:
- Keep UI simple; no separate route.

---

## TODO (needs product decisions)
- Decide whether CaseDetail tabs should embed CRUD UIs or link out to module queues.
- Confirm the minimal field set for Case create/edit forms (MVP1) beyond list/detail display.
- Confirm which pages must exist as separate routes vs dialogs (documents new/detail, task detail, payment/offset screens).
