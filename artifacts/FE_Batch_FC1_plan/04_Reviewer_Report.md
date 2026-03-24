# FC1 — Reviewer Report

**Batch**: FC1 — DocTemplate Admin UI
**Reviewer**: reviewer agent
**Date**: 2026-02-27
**Verdict**: PASS

---

## Acceptance Criteria Checklist

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| AC-1 | DocTemplate, DocTemplateCreatePayload, DocTemplateUpdatePayload, DocTemplateListParams types exist in documents.types.ts | ✅ | Lines 57-110. All 4 interfaces present with correct field types matching backend schema 1:1. |
| AC-2 | getDocTemplates(), getDocTemplate(), createDocTemplate(), updateDocTemplate() exist in documents.ts | ✅ | Lines 163-197. All 4 functions present with correct HTTP methods (GET/POST/PUT) and endpoint paths (`/doc-templates`). |
| AC-3 | DocTemplateList.vue renders table with columns: code, name, direction, status_effect, deadline_template_code, fee_draft_type, need_reply, enabled | ✅ | Lines 25-56. All 8 columns present with correct Chinese labels (编码, 名称, 方向, 状态变更, 期限模板, 费用类型, 需回复, 状态) plus an 操作 column (line 57). |
| AC-4 | Create dialog opens with blank form, requires code + name | ✅ | `openCreate()` (line 282) calls `resetForm()` and sets `isEdit=false`. `formRules` (lines 235-238) validates code + name as required. |
| AC-5 | Edit dialog opens with pre-filled data, code field disabled | ✅ | `openEdit(row)` (line 289) populates all fields from row data. Code input has `:disabled="isEdit"` (line 101). |
| AC-6 | deadline_template_code dropdown populated from TaskTemplate list | ✅ | `fetchTaskTemplates()` (line 254) calls `getTaskTemplates(true)`. `el-select` (lines 140-148) iterates `taskTemplateOptions` using `code` as value and `name` as label. |
| AC-7 | Toggle enabled button works | ✅ | `handleToggleEnabled()` (line 355) calls `updateDocTemplate(row.id, { enabled: !row.enabled })`, shows success message, and refreshes list. Toggle button text dynamically shows 停用/启用 (line 65). |
| AC-8 | Pagination works for template list | ✅ | `el-pagination` (lines 75-83) bound to `currentPage`, `pageSize`, `total`. `handlePageChange` (line 262) updates page and re-fetches. Pagination conditionally shown with `v-if="total > pageSize"`. |
| AC-9 | Route /system/doc-templates exists and loads DocTemplateList | ✅ | Router lines 206-211: `path: 'system/doc-templates'`, `name: 'system_doc_templates'`, lazy-loads `DocTemplateList.vue` with `requiredPerms: [Perms.SETTINGS_READ]`. |
| AC-10 | Menu item "文件模板" appears under system settings | ✅ | `menu.ts` line 60: `{ key: 'doc_templates', label: '文件模板', icon: '📄', route: '/system/doc-templates', requiredPerms: [Perms.SETTINGS_READ] }` in the `settings` group. |
| AC-11 | npm run lint passes | ✅ | Confirmed by quality gate agent. |
| AC-12 | npm run typecheck passes | ✅ | Confirmed by quality gate agent. |
| AC-13 | npm run build passes | ✅ | Confirmed by quality gate agent. |
| AC-14 | No files outside the 5-file allowlist were modified | ✅ | Only the 5 specified files were touched: `documents.types.ts`, `documents.ts`, `DocTemplateList.vue` (new), `router/index.ts`, `menu.ts`. |

---

## Code Quality Notes

### Positive Observations

1. **Type safety**: All interfaces match backend schemas exactly (DocTemplateOut, DocTemplateCreateIn, DocTemplateUpdateIn). Field types use proper union literals (`'IN' | 'OUT'`), nullable fields use `string | null` / `boolean | null`.

2. **Relative imports only**: All imports use `../../../api/...` pattern — no `@/` aliases. Verified in DocTemplateList.vue lines 198-203.

3. **Chinese UI labels throughout**: Page title "文件模板管理", all column labels, dialog titles, form labels, validation messages, success/error messages, empty state text, and direction tags (收文/发文) are all in Chinese.

4. **JSON placeholder text**: `fee_item_list` textarea has placeholder `[{"fee_code":"REG_FEE","fee_name":"登记费","amount":200}]` (line 173). `input_fields` textarea has placeholder `{"field_name":{"label":"字段标签","type":"text"}}` (line 181).

5. **Direction tags**: Table renders `el-tag` with `收文` (default) / `发文` (warning type) for IN/OUT respectively (lines 28-33).

6. **Follows TaskTemplateList.vue pattern**: Same page structure (page-container, page-header, error banner, table, dialog), same form validation pattern, same toggle mechanism, same error handling with `ApiErrorBanner`.

7. **Pagination added correctly**: Unlike TaskTemplateList (which uses a flat array), DocTemplateList correctly implements paginated fetching with `el-pagination` component, matching the backend's `PageResult[DocTemplateOut]` response format.

8. **Smart UX decisions**:
   - `enabled` switch only shown in edit mode (line 119: `v-if="isEdit"`) — new templates default to enabled
   - `code` field disabled on edit — matches backend constraint that code is immutable
   - Dialog has `close-on-click-modal="false"` to prevent accidental data loss
   - `v-model.trim` on text inputs to clean whitespace

9. **Error handling**: Uses `ApiErrorBanner` for list errors, `ElMessage.error` for dialog save errors with fallback message `'操作失败'`.

10. **Clean API layer**: No unnecessary mapping layer — backend DocTemplate fields used directly (unlike Document which requires field renaming). Types imported separately from functions via `documents.types.ts`.

### Minor Observations (Non-blocking)

1. **TaskTemplate fetch failure silent**: `fetchTaskTemplates()` has an empty catch block (line 257-258). This is intentional per the comment ("Silently fail — dropdown will be empty"), which is acceptable for an optional dropdown.

2. **No search/filter UI**: The `DocTemplateListParams` type supports `q`, `direction`, and `enabled` query params, but the list page doesn't expose filter controls. This is consistent with the architect plan scope and is a potential future enhancement.

---

## Risks / Issues

No blocking issues found.

| # | Item | Severity | Notes |
|---|------|----------|-------|
| 1 | No JSON validation for fee_item_list / input_fields | INFO | Architect plan explicitly scoped this out (Risk R2). Backend stores as plain text. Future enhancement. |
| 2 | No search/filter bar on list page | INFO | Types support it; UI can be added later. Current scope is basic CRUD. |

---

## Dependency Verification

All cross-module imports verified:
- `TaskTemplate` interface exists in `tasks.types.ts` (line 53) with `code` and `name` fields
- `getTaskTemplates()` function exists in `tasks.ts` (line 142) with `enabledOnly` parameter
- `ApiError` interface exists in `types.ts` (line 29)
- `ApiErrorBanner.vue` component exists at `components/errors/ApiErrorBanner.vue`
- `Pagination<T>` type exists in `types.ts` (used by `getDocTemplates` return type)

---

## Verdict

**PASS** — All 14 acceptance criteria met. Implementation follows the architect plan precisely, matches existing codebase patterns, uses correct Chinese labels, and passes all quality gates (lint, typecheck, build). No scope violations detected. Code is clean, well-structured, and type-safe.
