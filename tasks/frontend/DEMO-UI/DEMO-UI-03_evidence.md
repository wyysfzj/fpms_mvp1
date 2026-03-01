# Evidence Log — DEMO-UI-03

## Task
- ID: DEMO-UI-03
- Title: 关系链 UX（客户→案件→文档→费用→账单）+ 可点击跳转 + 面包屑链路
- Date: 2026-02-10
- Agent/Model: Claude Opus 4.6

## File Allowlist
- ✅ Confirmed all changes are within allowlist
- `frontend/src/components/relations/RelationChainCard.vue` — **new**
- `frontend/src/stores/pageContext.ts` — **new**
- `frontend/src/styles/relations.css` — **new**
- `frontend/src/components/header/TopHeader.vue` — updated (pageContext breadcrumb)
- `frontend/src/modules/cases/pages/CaseDetail.vue` — updated (RelationChainCard + breadcrumb)
- `frontend/src/modules/documents/pages/DocumentDetail.vue` — updated (same)
- `frontend/src/modules/fees/pages/FeeDraftDetail.vue` — updated (same)
- `frontend/src/modules/billing/pages/BillDetail.vue` — updated (same)
- `frontend/src/main.ts` — updated (import relations.css)

## Commands Executed
```bash
cd frontend
npm run lint       # ✅ pass
npm run typecheck  # ✅ pass
npm run build      # ✅ pass (1645 modules, 2.88s)
```

## Key Outputs
- lint: 0 warnings, 0 errors
- typecheck: 0 errors
- build: ✓ 1645 modules transformed, built in 2.88s
- RelationChainCard extracted as shared chunk: RelationChainCard.vue...js (2.16 kB)

## Changes Summary

### RelationChainCard.vue (new)
- Props: `client?`, `caseRef?`, `document?`, `feeDraft?`, `bill?` (each optional EntityRef)
- Renders chain items separated by "→" arrows
- Each item is a `<router-link>` when `id` exists, else shows "未关联" muted text
- Routes verified against actual router definitions:
  - client → `/clients/${id}/edit`
  - case → `/cases/${id}`
  - document → `/documents/${id}`
  - feeDraft → `/fees/drafts/${id}`
  - bill → `/billing/bills/${id}`
- `hasAnyLink` computed: hides entire card if no linked entities
- `truncateId()`: displays first 8 chars of UUID for readability

### pageContext.ts (new)
- Pinia store with `breadcrumb: string[]` and `title: string`
- Actions: `setBreadcrumb()`, `setTitle()`, `clear()`
- Used by detail pages to set contextual breadcrumbs

### TopHeader.vue (updated)
- When `pageContext.breadcrumb` has items: renders breadcrumb with "/" separators
- Otherwise: falls back to route-name-based Chinese breadcrumb (from DEMO-UI-01)

### Detail Pages Updated (4 pages)
Each page now:
1. Imports `RelationChainCard` and `usePageContext`
2. After data loads: calls `pageContext.setBreadcrumb([...])` with Chinese path
3. Renders `<RelationChainCard ... />` near top of content area
4. Calls `pageContext.clear()` in `onBeforeUnmount`

| Page | Breadcrumb | Chain Props |
|------|-----------|-------------|
| CaseDetail | 案件管理 / 案件详情 / {case_no} | client + case |
| DocumentDetail | 案件管理 / 文档详情 / {doc_type or id} | case + document |
| FeeDraftDetail | 费用管理 / 费用草稿 / {id[0:8]} | client + case + feeDraft |
| BillDetail | 账单管理 / 账单详情 / {bill_no or id} | client + case + bill |

### relations.css (new)
- `.relation-chain-card`: flex layout, uses CSS variables for theming
- `.chain-link`: primary color, underline on hover
- `.chain-muted`: subdued italic for unlinked items

## Data Availability (verified)
| Detail Page | client_id | case_id | Other |
|-------------|-----------|---------|-------|
| CaseDetail | ✅ available | self | client_name may be undefined |
| DocumentDetail | ❌ not in type | ✅ available | case_no may be undefined |
| FeeDraftDetail | ✅ available | ✅ available | — |
| BillDetail | ✅ available | ⚠️ mapped in frontend | client_name, case_no mapped |

## Manual Verification
### Steps
1. Open each detail page → see relation chain card at top
2. Click linked entities → navigates to correct detail page
3. Check header breadcrumb updates with page context
4. Navigate away → breadcrumb clears (reverts to default)
5. Verify no crash when relationship fields are missing

### Results
- Gates: PASS

## UI Reference Alignment Notes
- Relation chain design is new (not in patent_ui.html) — aligned to style-b tokens
- Breadcrumb approach: page-driven (set after data load), not router-driven
- `onBeforeUnmount` pattern used for cleanup (vs router.beforeEach approach avoided due to import timing)
- Tokens safety (variables.css base block unchanged): ✅

## Notes
- Used `caseRef` as prop name (not `case`) to avoid JavaScript reserved word conflict
- router/index.ts was NOT modified for pageContext clearing — cleanup done in each page's `onBeforeUnmount`
