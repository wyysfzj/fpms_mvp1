# Wave 47 Contract Freeze

## Task Scope
- Wave: `47`
- Role: Architect / Designer
- Frozen tasks (cumulative in this wave doc):
  - `tasks/postenhancement/frontend/PE-FE-AN-05.md`
  - `tasks/postenhancement/frontend/PE-FE-CS-01.md`
  - `tasks/postenhancement/frontend/PE-FE-CS-02.md`
- Current execution freeze: `PE-FE-CS-02`
- Scope boundaries are defined per task section; no product code changes.

## Global FE Conventions (Mandatory)
- Keep API access through typed client modules under `frontend/src/api`.
- Keep backend wire keys in `snake_case`; no ad-hoc key renaming.
- Reuse existing normalized API error handling flow (`http.ts` + normalized error object).
- All user-facing text MUST be Simplified Chinese.

## PE-FE-AN-05 Freeze (官费清单 + 缴费登记页面)

### Task / Allowlist
- Task ID: `PE-FE-AN-05`
- Task file: `tasks/postenhancement/frontend/PE-FE-AN-05.md`
- In-scope files for implementation:
  - `frontend/src/api/govPayments.ts` (new)
  - `frontend/src/api/govPayments.types.ts` (new)
  - `frontend/src/modules/annuity/pages/PayList.vue` (new)
  - `frontend/src/modules/annuity/pages/GovPaymentCreate.vue` (new)
- Out of scope:
  - any backend/model/schema/migration edits
  - router/menu/product-domain wiring changes outside allowlist
  - any cross-module refactor

### API Binding Contract (`frontend/src/api/govPayments.ts`)
- `createPayListFromFeeItems(payload)` -> `POST /pay-lists/from-fee-items`
  - request payload:
    - `fee_item_ids: string[]` (required, non-empty)
    - `planned_pay_date?: string` (`YYYY-MM-DD`)
    - `remark?: string`
  - response shape:
    - `summary`: `requested`, `success`, `failed`, `pay_list_created`
    - `pay_list`: `{ id, pay_list_no, client_id, currency, status, planned_pay_date, total_amount } | null`
    - `success[]`: `{ fee_item_id, case_id, amount, currency, pay_list_id }`
    - `failed[]`: `{ fee_item_id, code, message, status_code }`
- `registerGovPayment(payload)` -> `POST /gov-payments`
  - request payload:
    - `pay_list_id: number` (required)
    - `fee_item_id: string` (required)
    - `paid_date?: string` (`YYYY-MM-DD`)
    - `paid_amount?: number | string` (must be > 0 when provided)
    - `official_receipt_no?: string`
    - `remark?: string`
  - response shape:
    - `gov_payment`: `{ id, pay_list_id, case_id, fee_item_id, status, currency, paid_date, paid_amount, official_receipt_no, remark }`
    - `pay_list`: `{ id, pay_list_no, status, paid_date, total_amount, currency, client_id }`

### Page Workflow Contract (`PayList.vue` + `GovPaymentCreate.vue`)
- `PayList.vue` must support query/display of gov-payment chain data needed for operation entry and status visibility.
- From `PayList.vue`, user can choose fee items and execute pay-list generation through `createPayListFromFeeItems`.
- On generation result:
  - summary counters must always render.
  - success/failed rows must be separately visible when present.
  - partial success (`summary.failed > 0`) is treated as completed result, not fake full failure.
- `GovPaymentCreate.vue` must submit official payment registration through `registerGovPayment`.
- On registration success, UI must show returned `gov_payment` and updated `pay_list.status` (`DRAFT`/`PARTIAL`/`PAID`) as backend truth.

### Error Mapping Contract
- Request-level mapping for both endpoints:
  - `400`: business validation message in Chinese.
  - `401/403`: authentication/permission-denied message in Chinese.
  - `404`: target resource missing message in Chinese.
  - `409`: conflict/duplicate-protection message in Chinese.
  - `422`: request validation message in Chinese.
  - unknown/network: generic Chinese failure message.
- Endpoint/code mapping (must preserve backend code semantics):
  - `POST /pay-lists/from-fee-items`:
    - `400` + `FEE_ITEM_REQUIRED` / `PAY_LIST_SCOPE_INVALID`
    - `404` + `FEE_ITEM_NOT_FOUND`
    - item-level `409` + `GOV_PAYMENT_DUPLICATE` may appear in `failed[]` while HTTP remains `200`.
  - `POST /gov-payments`:
    - `404` + `PAY_LIST_NOT_FOUND` / `FEE_ITEM_NOT_FOUND`
    - `400` + `FEE_ITEM_REQUIRED` / `PAY_LIST_SCOPE_INVALID` / `GOV_PAYMENT_INVALID`
    - `409` + `GOV_PAYMENT_DUPLICATE`
- UI must never present failed requests as success.

### Permission Contract
- Pay-list generation operation is permission-gated by backend permission `PayList.Create`.
- Gov-payment registration operation is permission-gated by backend permission `GovPayment.Create`.
- Frontend permission visibility control is optional UX optimization only; backend `401/403` remains authoritative and must be handled.

### Simplified Chinese UI Text (Iron Rule)
- All user-visible text introduced/updated in AN-05 scope must be Simplified Chinese:
  - page title and section labels
  - filter labels/placeholders
  - action buttons
  - table/list headers
  - validation, success, conflict, and generic failure messages
  - empty-state/helper text
- English is allowed only for non-UI technical values (ids, enum/code values, API field names).

## Acceptance Checklist (AN-05)
- [ ] Implementation edits stay inside AN-05 allowlist only.
- [ ] API client implements frozen request/response contracts for both endpoints.
- [ ] Pay-list generation supports mixed success/failure receipt rendering per contract.
- [ ] Gov-payment registration reflects returned pay-list status as source of truth.
- [ ] Error handling follows frozen status/code mapping with Chinese user messaging.
- [ ] All user-visible text introduced/changed by AN-05 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`

## PE-FE-CS-01 Freeze (顾问/检索项目立案页)

### Task / Allowlist
- Task ID: `PE-FE-CS-01`
- Task file: `tasks/postenhancement/frontend/PE-FE-CS-01.md`
- Scope boundary: consulting/search case creation chain only (`frontend/src/api/consulting.ts` + `frontend/src/api/consulting.types.ts` + `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue`)
- In-scope files for implementation:
  - `frontend/src/modules/consulting/pages/ConsultingCaseCreate.vue` (new)
  - `frontend/src/api/consulting.ts` (new)
  - `frontend/src/api/consulting.types.ts` (new)
- Out of scope:
  - backend/schema/migration changes
  - edits outside task allowlist
  - cross-module refactors and product-level behavior changes

### API Binding Contract (`frontend/src/api/consulting.ts`)
- `createConsultingCase(payload)` -> `POST /consulting/cases`
  - request payload keys (backend `snake_case`, no alias drift):
    - `case_no: string` (required, non-empty)
    - `case_type: 'CONSULTING' | 'SEARCH'` (required)
    - `client_id: string` (required, non-empty)
    - `title_cn: string` (required, non-empty)
    - `primary_agent_id: string` (required, non-empty)
    - `recv_date: string` (`YYYY-MM-DD`, required)
  - response shape (`201 Created`):
    - `{ id, case_no, case_type, status, client_id, title_cn, primary_agent_id, recv_date, created_at }`
- API module should expose clear payload/result typings in `consulting.types.ts` and preserve raw backend field names (`title_cn`, `recv_date`).

### Page Workflow Contract (`ConsultingCaseCreate.vue`)
- Page must support creating exactly two project types: `CONSULTING` and `SEARCH`.
- Submit flow:
  - collect required fields and call `createConsultingCase`.
  - prevent duplicate submissions while request is in-flight.
  - on `201`, show Chinese success feedback and perform deterministic success navigation (case detail or case list path used by current project routing).
- Validation contract:
  - frontend must block empty required fields before submit.
  - frontend must restrict `case_type` to `CONSULTING/SEARCH`.
  - backend business validation response remains authoritative.

### Error Mapping Contract
- Request-level mapping for `POST /consulting/cases`:
  - `400` + `CONSULTING_CASE_INVALID`: show Chinese business validation message (required field/type/date semantics).
  - `401`: show login/auth message in Chinese.
  - `403`: show permission-denied message in Chinese.
  - `409` + `CASE_NO_DUPLICATE`: show duplicate-case-no message in Chinese.
  - `422`: show parameter validation message in Chinese (for example malformed `recv_date`).
  - unknown/network: generic Chinese failure message.
- Failure handling must keep form state stable and must not present fake success.

### Permission Contract
- Create operation is permission-gated by backend permission `ConsultingCase.Create`.
- Frontend visibility/route guarding is optional UX layer; backend `401/403` handling is mandatory.

### Simplified Chinese UI Text (Iron Rule)
- All user-visible text introduced/updated in CS-01 scope must be Simplified Chinese:
  - page title
  - form labels/placeholders
  - submit/cancel actions
  - validation and error messages
  - success feedback
- English is allowed only for technical values (`CONSULTING`, `SEARCH`, ids, API field names).

## Acceptance Checklist (CS-01)
- [ ] Implementation edits stay inside CS-01 allowlist only.
- [ ] API client/types implement frozen `POST /consulting/cases` payload + `201` response contract.
- [ ] Create page supports `CONSULTING` and `SEARCH` creation flow with deterministic submit/feedback behavior.
- [ ] Validation and error handling follow frozen status/code mapping with Chinese user messaging.
- [ ] All user-visible text introduced/changed by CS-01 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`

## PE-FE-CS-02 Freeze (支出录入与列表页)

### Task / Allowlist
- Task ID: `PE-FE-CS-02`
- Task file: `tasks/postenhancement/frontend/PE-FE-CS-02.md`
- Scope boundary: expense entry/list chain only (`frontend/src/api/expenses.ts` + `frontend/src/api/expenses.types.ts` + `frontend/src/modules/expenses/pages/ExpenseList.vue` + `frontend/src/modules/expenses/pages/ExpenseCreate.vue`)
- In-scope files for implementation:
  - `frontend/src/modules/expenses/pages/ExpenseList.vue` (new)
  - `frontend/src/modules/expenses/pages/ExpenseCreate.vue` (new)
  - `frontend/src/api/expenses.ts` (new)
  - `frontend/src/api/expenses.types.ts` (new)
- Out of scope:
  - backend/schema/migration changes
  - router/menu/product-domain edits outside allowlist
  - cross-module refactors and unrelated UI rewrites

### API Binding Contract (`frontend/src/api/expenses.ts`)
- `createExpense(payload)` -> `POST /expenses`
  - request payload keys (backend `snake_case`, no alias drift):
    - required: `case_id`, `category`, `expense_date`, `amount`
    - optional: `client_id`, `expense_no`, `vendor_name`, `currency`, `tax_amount`, `remark`
  - response (`201 Created`) shape:
    - `{ id, expense_no, case_id, category, expense_date, amount, currency, status, remark, created_at, updated_at }`
  - backend semantics to preserve:
    - default `currency` falls back to `CNY` when omitted.
    - default `status` is `DRAFT`.
    - backend may auto-generate `expense_no` when not provided.
- `getExpenses(params)` -> `GET /expenses`
  - query params:
    - core filter: `case_id`, `category`, `date_from`, `date_to`
    - optional extension: `currency`, `status`, `q`, `include_stats`
    - pagination: `page`, `page_size`
  - response shape:
    - base: `{ items, page, page_size, total }`
    - with `include_stats=true`: additional `stats` object
      - `count_by_category`, `sum_by_category`, `count_total`, `sum_total`

### Page Workflow Contract (`ExpenseList.vue` + `ExpenseCreate.vue`)
- `ExpenseList.vue`:
  - must support filtering at least by task acceptance dimensions: `case_id`, `category`, time range (`date_from/date_to`).
  - pagination behavior must follow backend `page/page_size/total`.
  - list rendering must be stable for empty state and error state.
  - category values must remain backend-compatible enum keys (`SEARCH_DB`, `TRANSLATION`, `TRANSPORT`, `OTHER`).
- `ExpenseCreate.vue`:
  - must submit create payload through `createExpense`.
  - submit must block duplicate in-flight requests.
  - on `201`, show Chinese success feedback and perform deterministic success navigation (return to list or detail path defined by implementation).
  - create flow must support both ordinary cases and consulting/search project cases through `case_id` entry.

### Validation & Error Mapping Contract
- Create endpoint (`POST /expenses`) mapping:
  - `400` + `EXPENSE_INVALID`: show Chinese validation/business message (required fields, category, date, amount/tax_amount constraints).
  - `404` + `CASE_NOT_FOUND`: show case-not-found message in Chinese.
  - `401`: show login/auth message in Chinese.
  - `403`: show permission-denied message in Chinese.
  - `422`: show request validation message in Chinese.
  - unknown/network: generic Chinese failure message.
- List endpoint (`GET /expenses`) mapping:
  - `400` + `EXPENSE_INVALID`: show Chinese filter validation message (for example invalid category/date range).
  - `401`: show login/auth message in Chinese.
  - `403`: show permission-denied message in Chinese.
  - `422`: show query validation message in Chinese.
  - unknown/network: generic Chinese failure message.
- UI must never display failed create/list requests as success.

### Permission Contract
- Create operation is permission-gated by backend permission `Expense.Create`.
- List/read operation is permission-gated by backend permission `Expense.Read`.
- Frontend permission display control is optional UX layer; backend `401/403` handling is mandatory.

### Simplified Chinese UI Text (Iron Rule)
- All user-visible text introduced/updated in CS-02 scope must be Simplified Chinese:
  - page title
  - filter labels/placeholders
  - table headers
  - form labels/placeholders
  - submit/cancel buttons
  - validation/success/error/empty-state messages
- English is allowed only for technical values (enum/code values, ids, API field names).

## Acceptance Checklist (CS-02)
- [ ] Implementation edits stay inside CS-02 allowlist only.
- [ ] API client/types implement frozen `POST /expenses` + `GET /expenses` payload/query/response contracts.
- [ ] List page supports case/category/date filtering with stable pagination behavior.
- [ ] Create page supports expense entry with deterministic submit and success feedback flow.
- [ ] Validation and error handling follow frozen status/code mapping with Chinese user messaging.
- [ ] All user-visible text introduced/changed by CS-02 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`
