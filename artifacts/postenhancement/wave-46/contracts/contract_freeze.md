# Wave 46 Contract Freeze

## Task Scope
- Wave: `46`
- Role: Architect / Designer
- Frozen tasks (this run):
  - `tasks/postenhancement/frontend/PE-FE-AN-04.md`
  - `tasks/postenhancement/frontend/PE-FE-CL-04.md`
  - `tasks/postenhancement/frontend/PE-FE-COM-04.md`
- Scope intent: freeze AN-04/CL-04/COM-04 UI behavior and API binding contracts for annuity batch drafts, bill bad-debt actions, and commission settlement workflow.

## Global FE Conventions (Mandatory)
- API calls must use existing typed client functions (for this wave: `frontend/src/api/annuity.ts`, `frontend/src/api/collections.ts`, `frontend/src/api/commission.ts`).
- Keep existing list/error/loading/pagination interaction patterns in affected modules.
- Backend wire keys remain `snake_case`; no ad-hoc field aliasing.
- All user-facing text MUST be Simplified Chinese.

## PE-FE-AN-04 Freeze (草单批量生成操作)

### Task / Allowlist
- Task ID: `PE-FE-AN-04`
- Task file: `tasks/postenhancement/frontend/PE-FE-AN-04.md`
- In-scope file for implementation:
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- Out of scope:
  - router wiring changes
  - other module pages/components
  - backend/schema/migration changes

### Batch Draft Generation Operation Contract
- Operation entry is in annuity task list page and acts on user-selected task rows.
- Request binding must use `generateAnnuityDrafts(payload)` from `frontend/src/api/annuity.ts`.
- Payload contract:
  - `task_ids`: number array from selected row `id` values (required, non-empty at submit time).
  - `pay_next_year`: optional boolean, defaults to `false` if UI does not explicitly set true.
  - `currency`: optional string; if provided, must pass through without key rename.
- Submit interaction contract:
  - no selection: block request and show Chinese prompt.
  - request in-flight: prevent duplicate submit.
  - completion (including partial success): render receipt details per contract below.

### Success/Failure Receipt Details Display Contract
- Receipt must be rendered from API response shape:
  - `summary`: `requested`, `targets`, `success`, `failed`, `pay_next_year`
  - `success[]`: `source_task_id`, `task_id`, `year_no`, `draft_id`, `currency`, `amount`, `pay_next_year`
  - `failed[]`: `source_task_id`, `task_id`, `year_no`, `pay_next_year`, `code`, `message`, `status_code`
- Display requirements:
  - summary counts are always visible after response.
  - success details and failure details are both visible when present.
  - `failed` list must show at least business code + message + status code for each failed row.
- Partial success semantics:
  - `failed > 0` does not invalidate `success` rows.
  - UI must present mixed result as completed receipt (not as fake all-or-nothing failure).

### Error Mapping Contract
- Transport/top-level API error mapping (request-level failure):
  - `400`: show business validation message in Chinese.
  - `401/403`: show authentication/permission message in Chinese.
  - `404`: show target/resource not found message in Chinese.
  - `409`: show conflict message in Chinese and keep current page state stable.
  - `422`: show parameter validation message in Chinese; field-level hint where applicable.
  - unknown/network: show generic Chinese failure message.
- Row-level failure mapping (from `failed[].status_code` + `failed[].code`):
  - `404` + `ANNUITY_TASK_NOT_FOUND`: indicate task (or next-year task) missing.
  - `409` + `ANNUITY_STATE_CONFLICT` / `ANNUITY_DRAFT_ALREADY_GENERATED`: indicate state conflict or duplicate generation.
  - other codes: show backend-provided failure message with Chinese user-facing wrapper text.

### Simplified Chinese UI Text (Iron Rule)
- All user-visible text introduced/updated in AN-04 scope must be Simplified Chinese:
  - batch action labels/buttons
  - selection validation prompts
  - receipt title/summary labels/column labels
  - success/failure feedback and error messages
- English is allowed only for non-UI technical values (ids, enum/code values, API field names).

## Acceptance Checklist (AN-04)
- [ ] Implementation edits stay inside AN-04 allowlist only.
- [ ] Batch operation is driven by selected task rows and bound to `generateAnnuityDrafts`.
- [ ] Receipt displays summary + success/failure detail rows per frozen response contract.
- [ ] Error handling follows frozen request-level and row-level mapping contract.
- [ ] All user-visible text introduced/changed by AN-04 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`

## PE-FE-CL-04 Freeze (账单坏账标记/恢复)

### Task / Allowlist
- Task ID: `PE-FE-CL-04`
- Task file: `tasks/postenhancement/frontend/PE-FE-CL-04.md`
- In-scope file for implementation:
  - `frontend/src/modules/billing/pages/BillDetail.vue`
- Out of scope:
  - router wiring changes
  - other module pages/components
  - backend/schema/migration changes

### Bad-Debt Mark/Restore UI Action Contract
- Action entry is in bill detail page and targets current `bill.id`.
- API binding contract:
  - mark action uses `markBillBadDebt(billId)` (`POST /bills/{bill_id}/bad-debt`).
  - restore action uses `restoreBillBadDebt(billId)` (`POST /bills/{bill_id}/bad-debt/restore`).
- Action availability contract:
  - when bill status is not `BAD_DEBT`, provide “标记坏账” action.
  - when bill status is `BAD_DEBT`, provide “恢复账单” action.
  - action submit must prevent duplicate in-flight submission.

### Permission / Visibility Contract
- Bad-debt actions are permission-gated by `BadDebt.Action`.
- Visibility behavior:
  - with permission: action controls are visible and interactive per status contract.
  - without permission: action controls must not be interactive (hidden or disabled with clear Chinese hint in-page).
- Security note:
  - frontend visibility control does not replace backend permission checks (`401/403` still handled).

### Post-Action State Visualization Contract
- After mark/restore success, bill state must refresh from backend source of truth (or equivalent deterministic local patch using response payload).
- UI status visualization must immediately reflect returned `status`:
  - mark success -> status becomes `BAD_DEBT` and action switches to restore mode.
  - restore success -> status becomes one of `UNSETTLED` / `PARTIALLY_SETTLED` / `SETTLED` based on backend restore logic.
- Amount/balance/status area in bill detail must remain consistent after action (no stale pre-action label).

### Error Mapping Contract
- Request-level API error mapping for mark/restore:
  - `400` + `BAD_DEBT_NOT_ALLOWED`: show “当前账单不满足坏账操作条件”类中文业务提示。
  - `401`: show login-expired Chinese message.
  - `403`: show permission-denied Chinese message.
  - `404` + `BILL_NOT_FOUND`: show bill-not-found Chinese message.
  - `409` + `BAD_DEBT_ALREADY_MARKED` / `BAD_DEBT_RESTORE_INVALID`: show conflict-state Chinese message.
  - `422`: show request validation Chinese message.
  - unknown/network: show generic Chinese failure message.
- Error handling must keep page state stable and never fake success on failed action.

### Simplified Chinese UI Text (Iron Rule)
- All user-visible text introduced/updated in CL-04 scope must be Simplified Chinese:
  - action buttons/confirm prompts
  - permission/forbidden hints
  - success feedback and error messages
  - status visualization helper text
- English is allowed only for non-UI technical values (ids, enum/code values, API field names).

## Acceptance Checklist (CL-04)
- [ ] Implementation edits stay inside CL-04 allowlist only.
- [ ] Bill detail supports bad-debt mark/restore actions with correct status-driven availability.
- [ ] Action visibility/interactivity is controlled by `BadDebt.Action` permission.
- [ ] Post-action state visualization refreshes and reflects backend status truth.
- [ ] Error handling follows frozen status/code mapping with Chinese user messaging.
- [ ] All user-visible text introduced/changed by CL-04 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`

## PE-FE-COM-04 Freeze (结算批次页)

### Task / Allowlist
- Task ID: `PE-FE-COM-04`
- Task file: `tasks/postenhancement/frontend/PE-FE-COM-04.md`
- In-scope file for implementation:
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue` (new)
- Out of scope:
  - router wiring changes
  - other module pages/components
  - backend/schema/migration changes

### Settlement Batch Page Workflow Contract
- Page must cover three core operations:
  - create settlement batch
  - generate settlement lines for selected batch
  - settlement report view (summary + breakdown + detail)
- API binding contract:
  - create batch: `createCommissionSettlement(payload)` -> `POST /commission/settlements`
  - generate lines: `generateCommissionSettlementLines(id)` -> `POST /commission/settlements/{id}/generate-lines`
  - report view: `getCommissionSettlementReport(params)` -> `GET /commission/reports/settlement`
- Create payload contract:
  - required: `agent_id`, `currency`
  - optional: `period_from`, `period_to`, `remark`
  - key names must remain backend-compatible `snake_case`

### Status/Statistics Visualization Contract
- Batch status visualization:
  - page must render batch `status` from backend response (`DRAFT` / `GENERATED` / other backend values) without alias drift.
  - unknown status must degrade safely (display raw status text; no runtime crash).
- Generate-lines result visualization:
  - after generate action, render and/or refresh by response fields:
    - `settlement_id`
    - `line_count`
    - `total_amount`
    - `created_count`
    - `updated_count`
    - `status`
- Report visualization contract:
  - totals section: `totals.line_count`, `totals.total_amount`
  - grouped statistics: `by_agent`, `by_case`, `by_time`
  - detail list: `details[]` including settlement/case/agent/amount/status/time fields
  - filters echo must follow returned `filters` object and selected query state.

### Permission / Operation Contract
- Operation permissions are endpoint-aligned:
  - create batch -> `CommissionSettlement.Create`
  - generate lines -> `CommissionSettlement.Action`
  - report view -> `CommissionReport.Read`
- If permission is missing, UI must not present fake-success behavior and must show Chinese permission feedback per error mapping.

### Error Mapping Contract
- Create batch (`POST /commission/settlements`) mapping:
  - `400` + `COMMISSION_SETTLEMENT_INVALID`: show Chinese business validation message.
  - `409` + `COMMISSION_SETTLEMENT_CONFLICT`: show Chinese conflict message (active scope duplicate).
  - `401/403`: show auth/permission Chinese message.
  - `422`: show validation Chinese message.
  - unknown/network: generic Chinese failure message.
- Generate lines (`POST /commission/settlements/{id}/generate-lines`) mapping:
  - `404` + `COMMISSION_SETTLEMENT_NOT_FOUND`: show Chinese not-found message.
  - `400` + `COMMISSION_SETTLEMENT_INVALID`: show Chinese business validation message.
  - `409` + `COMMISSION_SETTLEMENT_CONFLICT`: show Chinese state-conflict message.
  - `401/403`: show auth/permission Chinese message.
  - `422`: show validation Chinese message.
  - unknown/network: generic Chinese failure message.
- Report query (`GET /commission/reports/settlement`) mapping:
  - `400` + `COMMISSION_REPORT_INVALID`: show Chinese filter/parameter message.
  - `401/403`: show auth/permission Chinese message.
  - `422`: show validation Chinese message.
  - unknown/network: generic Chinese failure message.

### Simplified Chinese UI Text (Iron Rule)
- All user-visible text introduced/updated in COM-04 scope must be Simplified Chinese:
  - page title
  - form labels/placeholders
  - operation buttons
  - status/statistics labels
  - table headers
  - success/failure/error feedback
  - empty-state/helper texts
- English is allowed only for non-UI technical values (ids, enum/code values, API field names).

## Acceptance Checklist (COM-04)
- [ ] Implementation edits stay inside COM-04 allowlist only.
- [ ] Page supports create batch, generate lines, and report view flows bound to frozen APIs.
- [ ] Batch status and statistics visualization follows frozen response fields and safe fallback rules.
- [ ] Error handling follows frozen endpoint/code mapping with Chinese user messaging.
- [ ] All user-visible text introduced/changed by COM-04 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`
