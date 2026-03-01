# AI‑EOS PROMPT — DEMO‑UI‑03
## Title
DEMO‑UI‑03: 关系链 UX（客户 → 案件 → 文档 → 费用 → 账单）+ 可点击跳转 + 面包屑链路

## Context
客户 Demo 需要“业务叙事”而不只是功能入口：用户应能在详情页一眼看到对象之间关系与来源，并能快速跳转。

## Objective (Closed-loop)
1) 新增可复用的关系链组件 `RelationChainCard`：
   - 显示：客户 → 案件 → 文档 → 费用 → 账单
   - 每一段可点击跳转（若缺少 id，则禁用并显示“未关联/未知”）
2) 将关系链卡片集成到至少 4 个关键详情页：
   - Case detail
   - Document detail
   - Fee draft detail
   - Bill detail
3) Demo 模式下增强 header 面包屑链路（best-effort）：
   - 显示类似：案件管理 / 案件详情 / <案件号>
   - 由页面在数据加载后设置 breadcrumb（避免猜测）
4) 不新增后端接口：如需要 clientName 等字段，优先使用现有 detail response；若缺失，显示占位但仍可跳转到列表页。

## Non‑Goals (hard)
- 不做复杂全局 i18n
- 不在所有页面都加，仅限关键详情页
- 不新增后端 API

## File Allowlist (ONLY modify/add these)
- `frontend/src/components/relations/RelationChainCard.vue` (new)
- `frontend/src/stores/pageContext.ts` (new; breadcrumb/title store for header)
- `frontend/src/components/layout/TopHeader.vue` (update: demo模式读取 pageContext breadcrumb)
- `frontend/src/modules/cases/pages/CaseDetail.vue` (update: render RelationChainCard; set breadcrumb)
- `frontend/src/modules/documents/pages/DocumentDetail.vue` (update: render RelationChainCard; set breadcrumb)
- `frontend/src/modules/fees/pages/FeeDraftDetail.vue` (update: render RelationChainCard; set breadcrumb)
- `frontend/src/modules/billing/pages/BillDetail.vue` (update: render RelationChainCard; set breadcrumb)
- `frontend/src/styles/relations.css` (new; card styling aligned to patent_ui tokens)
- `frontend/src/main.ts` (update ONLY if needed to import relations.css globally)
- Evidence:
  - `task/frontend/DEMO-UI/DEMO-UI-03_evidence.md`

If more files are needed: STOP and propose smallest follow-up task.

## Implementation Steps
### 1) RelationChainCard component
- Props (best-effort):
  - `client?: { id: string; name?: string }`
  - `case?: { id: string; no?: string; title?: string }`
  - `document?: { id: string; refNo?: string }`
  - `feeDraft?: { id: string; label?: string }`
  - `bill?: { id: string; no?: string }`
- Render as a compact card:
  - left label: “关系链”
  - chain items separated by “→”
  - each item is a link when id exists; else muted text
- Links should navigate using router:
  - client -> `/clients/<id>/edit` (if that is the existing client detail route)
  - case -> `/cases/<id>`
  - document -> `/documents/<id>`
  - fee drafts -> `/fees/drafts/<id>` (or your actual route)
  - bill -> `/billing/bills/<id>` (or your actual route)

If route differs, use the project’s router definitions (do not invent).

### 2) pageContext store for breadcrumb
- Create `frontend/src/stores/pageContext.ts`:
  - state: `breadcrumb: string[]`, `title?: string`
  - actions: `setBreadcrumb([...])`, `clear()`
- Update `TopHeader.vue` in DEMO mode:
  - if breadcrumb exists: render “A / B / C” style string similar to patent_ui
  - else fallback to existing breadcrumb logic

### 3) Integrate into detail pages
For each of the 4 pages:
- After loading entity data:
  - compute best-effort breadcrumb:
    - Case detail: `["案件管理", "案件详情", case_no]`
    - Document detail: `["案件管理", "文档详情", ref_no or doc id]`
    - Fee draft detail: `["费用管理", "费用草稿", draft id]`
    - Bill detail: `["账单管理", "账单详情", bill id/no]`
- Render `<RelationChainCard ... />` near the top of content area.

### 4) Manual Verification
- Open each detail page:
  - see relation chain card
  - clicking links navigates correctly
  - header breadcrumb updates (demo mode)
- Confirm no page crashes when some relationship fields are missing.

## Gates (mandatory)
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

## Evidence Log (mandatory)
Write `task/frontend/DEMO-UI/DEMO-UI-03_evidence.md`:
- screenshots: 4 pages showing relation card + breadcrumb
- note any missing data fields and how UI degrades safely
- gates outputs
