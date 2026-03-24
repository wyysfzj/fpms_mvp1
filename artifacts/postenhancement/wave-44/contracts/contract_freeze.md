# Wave 44 Contract Freeze

## Task Scope
- Wave: `44`
- Role: Architect / Designer
- Frozen tasks:
  - `tasks/postenhancement/frontend/PE-FE-AN-02.md`
  - `tasks/postenhancement/frontend/PE-FE-CL-02.md`
  - `tasks/postenhancement/frontend/PE-FE-COM-02.md`
- Scope intent: freeze UI behavior and API binding contracts for annuity task list, dunning batch create, and commission rule management.

## Global FE Architecture Conventions (Mandatory)
- API access:
  - use existing `frontend/src/api/http.ts` interceptor pipeline only
  - consume typed functions from existing API clients (`annuity.ts`, `collections.ts`, `commission.ts`)
  - do not bypass clients with ad-hoc `axios` calls in pages
- Page behavior baseline:
  - loading state via `LoadingBlock`
  - error state via `ApiErrorBanner`
  - empty state via `EmptyState` where list result can be empty
  - paged list uses `PaginationBar` and backend `Pagination<T>` (`items/page/page_size/total`)
- Query/body key conventions:
  - backend wire keys keep `snake_case`
  - no client-side key renaming that breaks API contracts
- Route conventions:
  - route entry must be added in `frontend/src/router/index.ts` only when task allowlist includes router
  - child routes under `/` + `MainLayout`, with `meta.requiredPerms` present (array form)
  - route `name` uses existing snake_case convention

## Strict Allowlist Isolation (Mandatory)
- `PE-FE-AN-02` allowlist only:
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue` (new)
  - `frontend/src/router/index.ts`
- `PE-FE-CL-02` allowlist only:
  - `frontend/src/modules/collections/pages/DunningCreate.vue` (new)
- `PE-FE-COM-02` allowlist only:
  - `frontend/src/modules/commission/pages/CommissionRuleList.vue` (new)
- Out of scope for this wave:
  - edits to shared components/stores/http stack/constants outside task allowlist
  - cross-task file sharing or helper extraction across modules
  - backend/schema/migration/test changes

## UI Text Iron Rule (Mandatory)
- All user-facing UI text must be Simplified Chinese:
  - page title, filter labels, table headers, buttons, dialog copy, validation/error/toast, empty-state text
- English is allowed only for technical values:
  - enum/code values, API fields, ids, routes, file paths
- For this wave, any new visible string introduced in the three new pages must be Chinese.

## PE-FE-AN-02 Freeze (Annuity Task List Page)

### Page/Route Contract
- Route entry is required in `frontend/src/router/index.ts` (this task includes router allowlist).
- Follow existing route entry conventions:
  - path under authenticated children (`/` -> child path)
  - deterministic snake_case route name
  - `meta.requiredPerms` array present
- AN module route should be the first annuity entry point and must not alter unrelated existing routes.

### API Binding Contract
- Data source: `getAnnuityTasks(params)` from `frontend/src/api/annuity.ts`.
- Query parameters supported by page filters/pagination:
  - `due_from`, `due_to`, `status`, `pending_mode`, `case_id`, `client_id`, `notice_status`, `page`, `page_size`
- Do not invent alternative filter keys.

### UI Behavior Contract
- Must provide:
  - filter area (at minimum supports status-related filtering and task-state scope)
  - paginated table/list rendering
  - status column with deterministic text display (backend status values mapped for users)
- Pagination behavior:
  - changing filter resets `page` to `1`
  - page/page_size changes trigger data refetch
- Status list behavior:
  - support backend-compatible status values without hardcoding incompatible aliases
  - unknown status must degrade safely (show original value, no runtime crash)

### Error/Status Semantics
- `GET /annuity/tasks`:
  - success `200`
  - business error `400`
  - auth/perm `401/403`
  - validation `422`
- Page must rely on normalized `ApiError` from interceptor and render non-blocking error UI.

## PE-FE-CL-02 Freeze (Dunning Batch Create Page)

### Page Contract
- Single create flow page for dunning generation.
- No router change in this task (allowlist excludes router file).

### API Binding Contract
- Create action binds to `generateDunning(payload)` from `frontend/src/api/collections.ts`.
- Payload contract (backend-aligned):
  - required cutoff date: `to_date` (UI label can be “截止日/到期截至日”)
  - customer scope: `client_id` and/or `client_ids`
  - optional status scopes: `include_statuses`, `exclude_statuses`
  - optional conflict mode: `strict_conflict`
- Contract note for requirement wording:
  - task requirement “due_date + customer filters” maps to backend `to_date + client scope`; UI wording can use “截止日”.

### Interaction Contract
- Submit flow:
  1. validate required date before request
  2. submit once per user action (loading lock to avoid double submit)
  3. success branch handles returned `summary + batches`
- Success navigation:
  - after successful create, redirect to detail or list (as task acceptance allows)
- Conflict branch:
  - when `strict_conflict=true`, handle `409` explicitly with user-readable Chinese message
- Validation branch:
  - `422`/field errors mapped to field-level hints where available

### Error/Status Semantics
- `POST /dunning`:
  - success `200`
  - business `400`, scope-not-found `404`, conflict `409`
  - auth/perm `401/403`
  - validation `422`

## PE-FE-COM-02 Freeze (Commission Rule Management Page)

### Page Contract
- One management page for rule list + create/edit + enable/disable interaction.
- No router change in this task (allowlist excludes router file).

### API Binding Contract
- Required client functions:
  - `getCommissionRules(...)`
  - `createCommissionRule(payload)`
  - `updateCommissionRule(ruleId, payload)`
- Enable/disable interaction contract:
  - toggle is implemented via `updateCommissionRule` with `enabled` patch only
  - no extra endpoint invention for enable/disable

### CRUD + Toggle Interaction Contract
- List:
  - supports pagination (`page`, `page_size`) and rule filters (`enabled`, `case_type`, `fee_type`, `q`)
- Create:
  - submits complete rule payload with backend field names
  - on success, list refreshes and new/updated row is visible
- Edit:
  - patch update uses rule id path param
  - preserves unchanged fields if UI does partial edit
- Enable/Disable:
  - user action flips current `enabled` state
  - success feedback in Chinese
  - list reflects latest state without full-page reload

### Error/Status Semantics
- `GET /commission/rules`: success `200`; auth/perm `401/403`; validation `422`
- `POST /commission/rules`: success `201`; business `400/409`; auth/perm `401/403`; validation `422`
- `PUT /commission/rules/{rule_id}`: success `200`; business `400/404/409`; auth/perm `401/403`; validation `422`

## Non-Regression Constraints
- No behavior drift outside these three task allowlists.
- Preserve existing FE architecture patterns for error/loading/pagination handling.
- Do not introduce mixed-language UI copy; all visible text remains Simplified Chinese.
- Keep API contract compatibility with frozen backend endpoints and status semantics.

## Acceptance Checklist
- [ ] Implementation for each task edits only its allowlisted files.
- [ ] `PE-FE-AN-02` delivers filters + pagination + status list and route entry via router conventions.
- [ ] `PE-FE-CL-02` delivers dunning create flow bound to cutoff-date + customer filters (`to_date` + client scope).
- [ ] `PE-FE-COM-02` delivers rule CRUD + enable/disable via `updateCommissionRule(enabled=...)`.
- [ ] All newly introduced user-facing strings in three pages are Simplified Chinese.
- [ ] Frontend implementation verification target:
  - `cd frontend && npm run lint && npm run typecheck`
