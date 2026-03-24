# Wave 48 Contract Freeze

## Task Scope
- Wave: `48`
- Role: Architect / Designer
- Frozen tasks (cumulative in this wave doc):
  - `tasks/postenhancement/frontend/PE-FE-CS-03.md`
  - `tasks/postenhancement/frontend/PE-FE-CS-04.md`
- Current execution freeze: `PE-FE-CS-04`
- Wave scope for this freeze: consulting fee draft create page + consulting profitability page.
- This execution is doc-only; no product code changes.

## Global FE Conventions (Mandatory)
- Enforce strict allowlist isolation for each atomic task.
- Keep backend wire keys in `snake_case`; do not introduce ad-hoc key aliasing.
- Reuse existing normalized API error flow (`frontend/src/api/http.ts`).
- All user-facing text MUST be Simplified Chinese.

## PE-FE-CS-03 Freeze (顾问/检索服务费草单生成页)

### Task / Allowlist
- Task ID: `PE-FE-CS-03`
- Task file: `tasks/postenhancement/frontend/PE-FE-CS-03.md`
- Dependency: `PE-BE-CS-05`
- In-scope file for implementation:
  - `frontend/src/modules/consulting/pages/ConsultingFeeDraftCreate.vue` (new)
- Out of scope:
  - backend/model/schema/migration/test changes
  - edits to router/menu wiring
  - edits to other pages/components/modules
  - edits to frontend API client/type files outside allowlist

### API Contract (`POST /consulting/fee-drafts`)
- Permission contract:
  - operation is permission-gated by backend `ConsultingFeeDraft.Create`.
  - frontend visibility control is optional UX layer; backend `401/403` is authoritative.
- Request payload contract:
  - `case_id: string` (required, non-empty)
  - `mode: 'FIXED' | 'HOURLY' | 'HYBRID'` (required)
  - `currency?: string` (optional, backend defaults to `CNY` when absent)
  - `fixed_fee?: number | string`
  - `hourly_lines?: Array<{ fee_code, fee_name, hours, hourly_rate, remark?, trace_key? }>`
  - `misc_lines?: Array<{ fee_code, fee_name, amount, remark?, trace_key? }>`
- Mode constraints (must be enforced by page submit flow):
  - `FIXED`: `fixed_fee > 0`; `hourly_lines` must be absent/empty.
  - `HOURLY`: `hourly_lines` required and non-empty; each line `hours > 0`, `hourly_rate >= 0`.
  - `HYBRID`: `hourly_lines` required and non-empty; `fixed_fee >= 0`; total generated amount must be `> 0`.
  - `misc_lines` are optional; if provided, each line `amount >= 0`.
- Response contract (`201 Created`):
  - `draft_id: string`
  - `draft_type: 'CONSULT_FEE' | 'SEARCH_FEE'`
  - `mode: 'FIXED' | 'HOURLY' | 'HYBRID'`
  - `currency: string`
  - `totals: { total_gov, total_service, total_misc, amount }`
  - `items[]: { item_id, fee_code, fee_name, fee_type, quantity, unit_price, amount, trace_key, remark }`
  - `created_line_count: number`

### Page Workflow Contract (`ConsultingFeeDraftCreate.vue`)
- Page must support three parameter modes end-to-end:
  - 固定模式（`FIXED`）
  - 工时模式（`HOURLY`）
  - 混合模式（`HYBRID`）
- UI interaction contract:
  - mode switch updates visible parameter section deterministically.
  - hourly/misc line editors support add/remove with stable index binding.
  - submit is locked while request is in-flight (no duplicate submission).
  - on `201`, show Chinese success feedback and deterministic post-submit behavior:
    - navigate to draft detail/list when route exists, or
    - remain on page and show returned draft summary/items snapshot.

### Error Mapping Contract
- Request-level mapping:
  - `400` + `CONSULTING_FEE_INVALID`: Chinese business-validation message.
  - `401`: Chinese unauthenticated/login-expired message.
  - `403`: Chinese permission-denied message.
  - `404` + `CASE_NOT_FOUND`: Chinese case-not-found message.
  - `409` + `FEE_DRAFT_CONFLICT`: Chinese conflict message; include existing `draft_id` when returned.
  - `422`: Chinese parameter validation message.
  - unknown/network: generic Chinese failure message.
- Failure handling contract:
  - keep current form state stable on failure.
  - never present failed requests as success.

### Simplified Chinese UI Text (Iron Rule)
- All user-visible text introduced/updated in CS-03 scope must be Simplified Chinese:
  - page title and section titles
  - mode labels and form labels/placeholders
  - line editor controls
  - submit/cancel actions
  - validation/success/error/conflict messages
  - empty/helper texts
- English is allowed only for technical values (ids, enum/code values, API field names).

## Acceptance Checklist (CS-03)
- [ ] Implementation edits stay inside CS-03 allowlist only.
- [ ] Page supports `FIXED` / `HOURLY` / `HYBRID` parameter input and submit flow.
- [ ] Request payload/response handling follows frozen `POST /consulting/fee-drafts` contract.
- [ ] Validation and error handling follow frozen status/code mapping with Chinese user messaging.
- [ ] All user-visible text introduced/changed by CS-03 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`

## PE-FE-CS-04 Freeze (顾问项目收益视图)

### Task / Allowlist
- Task ID: `PE-FE-CS-04`
- Task file: `tasks/postenhancement/frontend/PE-FE-CS-04.md`
- Dependency: `PE-BE-CS-06`
- In-scope file for implementation:
  - `frontend/src/modules/consulting/pages/ConsultingProfitability.vue` (new)
- Out of scope:
  - backend/model/schema/migration/test changes
  - router/menu wiring edits
  - edits to other pages/components/modules
  - edits to frontend API client/type files outside allowlist

### Data Source Contract (Reuse Existing API Clients)
- Core KPI data must be aggregated by `case_id` using existing clients:
  - `getCaseReceipts(case_id)` -> `GET /cases/{case_id}/receipts`
  - `getExpenses({ case_id, include_stats: true, ... })` -> `GET /expenses`
- Optional settlement-candidate panel (non-core KPI):
  - `getCommission({ case_id, ... })` -> `GET /commission`
- Contract note:
  - CS-04 implementation must not create new API client files/endpoints in this atomic task.

### Project KPI Contract (收入/支出/毛利)
- Query dimension:
  - project id (`case_id`) is required for each KPI query execution.
- KPI formulas (core):
  - `收入（已收） = case_receipt.total_paid`
  - `支出（累计） = expenses.stats.sum_total` (fallback to `sum(items.amount)` if stats absent)
  - `毛利 = 收入（已收） - 支出（累计）`
- Supplementary values shown on page:
  - `应收合计 = case_receipt.total_billed`
  - `未收余额 = case_receipt.total_outstanding`
- Number/currency rendering:
  - use two-decimal display for amount fields.
  - amount display currency follows backend returned currency context.

### Page Workflow Contract (`ConsultingProfitability.vue`)
- Must provide deterministic load flow:
  1. user inputs/selects `case_id`.
  2. page requests core KPI data sources.
  3. page renders KPI cards for 收入/支出/毛利 and project summary metrics.
- Interaction constraints:
  - re-query lock while request is in-flight (prevent duplicate trigger).
  - changing `case_id` must trigger full KPI recomputation.
  - empty-state and error-state must be explicitly rendered; no silent blank page.
- If optional commission panel is implemented:
  - render it as auxiliary data area; it must not replace or redefine core KPI formulas above.

### Error Mapping Contract
- `GET /cases/{case_id}/receipts`:
  - `404` + `CASE_RECEIPT_NOT_FOUND`: treat as "暂无收款记录" and use 收入=0、应收=0、未收=0 (non-blocking).
  - `401/403`: Chinese auth/permission message.
  - `422`: Chinese parameter validation message.
- `GET /expenses`:
  - `400` + `EXPENSE_INVALID`: Chinese filter/business validation message.
  - `401/403`: Chinese auth/permission message.
  - `422`: Chinese parameter validation message.
- `GET /commission` (only when optional panel enabled):
  - `400` + `COMMISSION_FILTER_INVALID`: Chinese filter validation message.
  - `401/403`: Chinese auth/permission message.
  - `422`: Chinese parameter validation message.
- unknown/network: generic Chinese failure message.
- Failure handling contract:
  - failed requests must not be shown as successful KPI results.
  - keep last stable query input and avoid UI crash.

### Permission Contract
- Core KPI read path depends on backend permissions:
  - `CaseReceipt.Read`
  - `Expense.Read`
- Optional commission panel depends on:
  - `Commission.Read`
- Frontend visibility control is optional UX layer; backend `401/403` handling remains mandatory.

### Simplified Chinese UI Text (Iron Rule)
- All user-visible text introduced/updated in CS-04 scope must be Simplified Chinese:
  - page title and KPI card labels
  - case query/filter labels and placeholders
  - refresh/query action labels
  - table/list/summary labels
  - validation/error/empty-state/helper messages
- English is allowed only for technical values (ids, enum/code values, API field names).

## Acceptance Checklist (CS-04)
- [ ] Implementation edits stay inside CS-04 allowlist only.
- [ ] Page supports case-level KPI query and shows 收入/支出/毛利 core metrics.
- [ ] KPI calculations follow the frozen formulas and backend field mapping.
- [ ] Error handling follows frozen status/code mapping with Chinese user messaging.
- [ ] Permission-denied states are handled without fake success.
- [ ] All user-visible text introduced/changed by CS-04 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`
