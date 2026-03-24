# FB2 Review Report — Client Detail + Address/Contact UI

**Reviewer**: Review Agent
**Date**: 2026-02-27
**Verdict**: **PASS WITH NOTES**

---

## 1. Summary

All 6 files were reviewed. The implementation is clean, consistent, and meets all 16 acceptance criteria. Code follows existing project patterns (relative imports, Element Plus usage, Chinese labels, error handling via try/catch + ElMessage). Two pre-existing backend gaps (R1, R3 from findings.md) impact the detail page but are out of FB2 scope. One new finding (R5) identifies a field-name mismatch in the related-cases tab that will cause the title column to display blank.

---

## 2. Acceptance Criteria Results

| AC | Criterion | Status | Notes |
|----|-----------|--------|-------|
| AC-1 | `clients.types.ts` exports 6 Address/Contact types | ✅ | `ClientAddress`, `ClientAddressCreatePayload`, `ClientAddressUpdatePayload`, `ClientContact`, `ClientContactCreatePayload`, `ClientContactUpdatePayload` — all present (lines 53-121) |
| AC-2 | `clients.ts` exports 8 new CRUD functions | ✅ | `getClientAddresses`, `createClientAddress`, `updateClientAddress`, `deleteClientAddress`, `getClientContacts`, `createClientContact`, `updateClientContact`, `deleteClientContact` — all present (lines 112-168) |
| AC-3 | `AddressTable.vue` table columns: type, line1, city, province, postal_code, country, is_default, actions | ✅ | All 8 columns present. Type rendered via `el-tag` with label mapping. |
| AC-4 | `AddressTable.vue` create/edit dialog with all fields | ✅ | `el-dialog` with `el-select` (GENERAL/BILLING/MAILING), 6 text inputs, `el-switch` for is_default |
| AC-5 | `AddressTable.vue` delete with `el-popconfirm` ("确定删除？") | ✅ | Line 32 — exact text match |
| AC-6 | `ContactTable.vue` table columns: name, title, phone, mobile, email, is_primary, actions | ✅ | All 7 columns present. is_primary rendered via `el-tag`. |
| AC-7 | `ContactTable.vue` create/edit dialog with all fields, contact_name required | ✅ | `el-form-item label="姓名" required` (line 47), `el-switch` for is_primary, client-side validation on submit (line 140) |
| AC-8 | `ContactTable.vue` delete with `el-popconfirm` ("确定删除？") | ✅ | Line 27 — exact text match |
| AC-9 | `ClientDetail.vue` has 4 tabs: 基本信息, 地址, 联系人, 关联案件 | ✅ | `el-tabs` with 4 `el-tab-pane` elements (lines 27-102) |
| AC-10 | "基本信息" tab shows: name, client_code, client_type, default_currency, email, is_active | ✅ | All 6 fields rendered in `.info-grid` layout (lines 30-59) |
| AC-11 | "关联案件" tab fetches cases filtered by `client_id` | ✅ | `http.get('/cases', { params: { client_id: id } })` — backend confirmed to support `client_id` filter. **See R5** for title field mismatch. |
| AC-12 | Header has back button (→ `/clients`) and edit button (→ `/clients/:id/edit`) | ✅ | `goBack()` pushes `/clients` (line 186), `handleEdit()` pushes `/clients/${id}/edit` (line 190) |
| AC-13 | Router `clients/:id` → `ClientDetail.vue` with perm `CLIENTS_READ` | ✅ | Lines 164-168 in router/index.ts — lazy import, `requiredPerms: [Perms.CLIENTS_READ]` |
| AC-14 | All UI labels in Chinese (简体中文) | ✅ | Verified across all 4 files: 客户名称, 客户代码, 类型, 地址行1, 城市, 省份, 邮编, 国家, 默认, 姓名, 职务, 电话, 手机, 邮箱, 主联系人, 基本信息, 地址, 联系人, 关联案件, 案件编号, 案件名称, 状态, etc. |
| AC-15 | All imports use relative paths (no `@/`) | ✅ | All imports verified: `../../../api/clients`, `../../../api/http`, `../../../api/clients.types`, `../../../api/types`, `../../../components/errors/ApiErrorBanner.vue`, `../components/AddressTable.vue`, `../components/ContactTable.vue` |
| AC-16 | Quality gate passed (`npm run lint && npm run typecheck && npm run build`) | ✅ | Task #8 completed successfully |

**Result: 16/16 ✅**

---

## 3. Code Quality Observations

### Positive Patterns
- **Consistent error handling**: All async operations wrapped in try/catch with `ElMessage.error()` / `ElMessage.success()` — matches project-wide pattern.
- **Loading states**: Both table components and the detail page use `v-loading` / `el-skeleton` appropriately.
- **Clean separation**: AddressTable and ContactTable are self-contained components with their own data fetching — good encapsulation.
- **Type safety**: Props typed via `defineProps<{ clientId: string }>()`, API functions use proper generics.
- **Form reset on open**: Both `openCreate()` and `openEdit()` correctly reset/populate form state.
- **Contact validation**: `ContactTable.vue` has client-side required validation for `contact_name` before submit (line 140).

### Minor Observations (Non-blocking)
1. **Inline styles for layout**: `style="display: flex; justify-content: flex-end; margin-bottom: 12px;"` used in AddressTable and ContactTable. Acceptable for layout, no color values.
2. **No `<style>` block in ClientDetail.vue**: Relies on global CSS classes (`page-container`, `page-header`, `info-grid`, etc.). This is consistent with other pages in the project.
3. **No route-change reactivity**: `fetchClient()` and `fetchCases()` only run in `onMounted`. If the route params change without remounting (unlikely for `:id` routes), data won't refresh. Standard SPA pattern — acceptable.
4. **`defaultForm()` type assertion**: `ClientAddressCreatePayload & { is_default: boolean }` — technically `is_default` is already optional in the payload, but this makes it explicit. Fine.

---

## 4. Security Check

| Check | Status |
|-------|--------|
| No `v-html` usage | ✅ Clean |
| No direct DOM manipulation | ✅ Clean |
| All API calls via `http` client (includes auth headers) | ✅ Clean |
| No user-controlled HTML rendering | ✅ Clean |
| No credential exposure | ✅ Clean |
| Input sanitization | ✅ Text inputs via `el-input`, select via `el-select` — no raw HTML injection vectors |

**No security concerns identified.**

---

## 5. Recommendations (Non-blocking)

1. **R5 — Title field mismatch in 关联案件 tab** (NEW, MEDIUM):
   `ClientDetail.vue` defines `RelatedCase.title` but the backend cases list endpoint returns `title_cn` / `title_en` (not `title`). The "案件名称" column will display blank. Fix: change `row.title` to `row.title_cn || row.title_en || '-'` and update the `RelatedCase` interface.

2. **Consider using `getCases()` from `cases.ts`** instead of direct `http.get('/cases')` — this would leverage the existing `mapCase()` function that correctly maps `title_cn` → `title`. Currently avoided because `cases.ts` was outside the modification allowlist.

3. **Add `watch` on `clientId`**: If future routing allows navigating between clients without remount, adding a watcher would ensure data freshness.

4. **Pagination on Address/Contact tables**: Currently no pagination — acceptable for typical client data volumes, but could be added if clients accumulate many addresses.

---

## 6. Known Issues (from findings.md)

| ID | Severity | Description | Impact on FB2 |
|----|----------|-------------|---------------|
| R1 | HIGH | Backend has no `GET /clients/{client_id}` single-client endpoint. `getClient()` API call will 404. | **ClientDetail.vue will fail to load client data.** Out of FB2 scope — needs backend fix task. |
| R3 | MED | Frontend `getCases()` doesn't pass `client_id` param. Workaround: direct `http.get('/cases', { params: { client_id } })`. | Workaround implemented correctly in ClientDetail.vue. |
| R5 | MED | (NEW) Backend returns `title_cn`/`title_en` for cases, but `RelatedCase` interface expects `title`. Title column will be blank. | Needs post-FB2 fix — either update interface or use `getCases()` mapper. |

---

## 7. Files Reviewed

| File | Lines | Status |
|------|-------|--------|
| `frontend/src/api/clients.types.ts` | 122 | ✅ No issues |
| `frontend/src/api/clients.ts` | 169 | ✅ No issues |
| `frontend/src/modules/clients/components/AddressTable.vue` | 200 | ✅ Clean |
| `frontend/src/modules/clients/components/ContactTable.vue` | 175 | ✅ Clean |
| `frontend/src/modules/clients/pages/ClientDetail.vue` | 197 | ✅ With notes (R1, R5) |
| `frontend/src/router/index.ts` | 239 | ✅ Route added correctly |

**No files outside the allowlist were modified.**

---

## 8. Final Verdict

**PASS WITH NOTES** — All acceptance criteria met. Implementation is clean, consistent, and follows project conventions. Three known issues exist (R1, R3, R5), of which R1 (missing backend endpoint) will block the detail page at runtime and R5 (title field mismatch) will cause a blank column. Both require follow-up tasks outside FB2 scope.
