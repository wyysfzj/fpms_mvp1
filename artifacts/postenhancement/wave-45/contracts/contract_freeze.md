# Wave 45 Contract Freeze

## Task Scope
- Wave: `45`
- Role: Architect / Designer
- Frozen tasks:
  - `tasks/postenhancement/frontend/PE-FE-AN-03.md`
  - `tasks/postenhancement/frontend/PE-FE-CL-03.md`
  - `tasks/postenhancement/frontend/PE-FE-COM-03.md`
- Scope intent: freeze UI behavior and API binding contracts for this wave, with AN-03 contract fixed first.

## Global FE Conventions (Mandatory)
- Keep API access through existing typed clients and interceptor stack.
- Keep list pages on existing loading/error/pagination patterns.
- Keep backend wire keys in `snake_case`; no ad-hoc key renaming.
- All user-facing text MUST be Simplified Chinese.

## PE-FE-AN-03 Freeze (客户指示编辑对话框)

### Task / Allowlist
- Task ID: `PE-FE-AN-03`
- Task file: `tasks/postenhancement/frontend/PE-FE-AN-03.md`
- In-scope files for implementation:
  - `frontend/src/modules/annuity/components/InstructionDialog.vue` (new)
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- Out of scope:
  - router wiring changes
  - other module pages/components
  - backend/schema/migration changes

### Instruction Dialog Behavior Contract (`PAY` / `ABANDON` / `DEFER`)
- Dialog must support and clearly expose exactly three instruction actions:
  - `PAY`
  - `ABANDON`
  - `DEFER`
- Selection behavior:
  - user must explicitly choose one action before save.
  - save control must prevent duplicate submit while request is in-flight.
- Payload behavior:
  - submit action must map to backend-compatible instruction value without alias drift.
  - task identity must be bound to the selected row/context and not inferred globally.

### Save Success -> List Refresh Contract
- On successful instruction save:
  - close dialog.
  - show Chinese success feedback.
  - refresh annuity task list using current filter + pagination state.
- Refresh semantics:
  - do not reset user filters unintentionally.
  - visible row state must reflect latest instruction/result from backend.

### Error Display Mapping Contract
- Error handling must use normalized frontend API error flow.
- Status/error mapping contract:
  - `400`: show business message (Chinese), keep dialog open for correction.
  - `401/403`: show auth/permission-denied message (Chinese), do not fake success.
  - `404`: show target-not-found message (Chinese), keep UI state consistent.
  - `409`: show conflict message (Chinese) and prompt user to refresh/retry path.
  - `422`: show validation message (Chinese), prioritize field-level hint if available.
  - unknown/network errors: show generic Chinese failure message.
- Error text must be user-facing Chinese; technical codes can remain in logs only.

### Simplified Chinese UI Text (Iron Rule)
- All visible dialog/list interaction text in AN-03 scope must be Simplified Chinese:
  - dialog title/content
  - action labels/buttons
  - validation/error/success messages
  - helper/empty-state text added by this task
- English is allowed only for non-UI technical values (`PAY/ABANDON/DEFER`, ids, API fields).

## Acceptance Checklist (AN-03)
- [ ] Implementation edits stay inside AN-03 allowlist only.
- [ ] Dialog behavior for `PAY/ABANDON/DEFER` is implemented per frozen interaction contract.
- [ ] Save success path closes dialog and refreshes task list with current query state.
- [ ] Error mapping follows frozen status semantics and Chinese user messaging.
- [ ] All user-visible text introduced/changed by AN-03 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`

## PE-FE-CL-03 Freeze (催款列表/详情页)

### Task / Allowlist
- Task ID: `PE-FE-CL-03`
- Task file: `tasks/postenhancement/frontend/PE-FE-CL-03.md`
- In-scope files for implementation:
  - `frontend/src/modules/collections/pages/DunningList.vue` (new)
  - `frontend/src/modules/collections/pages/DunningDetail.vue` (new)
- Out of scope:
  - router wiring changes
  - other module pages/components
  - backend/schema/migration changes

### Query + Filter Contract (轮次 / 状态)
- Dunning list must support query/filter behavior for:
  - `round` (轮次)
  - `status` (状态)
- Filter contract:
  - UI filter fields must map to backend-compatible query keys without alias drift.
  - filter submit triggers list refetch.
  - changing filter resets `page` to `1`.
  - pagination changes keep current filter conditions.

### Row Detail Display Contract
- List row must provide deterministic detail entry action (view details).
- Detail page/area must render row-linked dunning data consistently:
  - batch/header core fields (e.g., round, status, client/time context)
  - line/detail records associated with selected row
- Row selection/detail binding must use the selected row identity; no cross-row leakage.

### Error Handling Contract
- Use normalized frontend API error flow and Chinese user-facing feedback.
- Status/error mapping contract:
  - `400`: business message (Chinese), page remains interactive.
  - `401/403`: auth/permission-denied message (Chinese).
  - `404`: dunning list/detail target-not-found message (Chinese).
  - `409`: conflict message (Chinese) where applicable.
  - `422`: validation message (Chinese), prioritize field hints when available.
  - unknown/network errors: generic Chinese failure message.
- Error display must not present raw English backend internals to end users.

### Simplified Chinese UI Text (Iron Rule)
- All user-visible text introduced/updated in CL-03 scope must be Simplified Chinese:
  - page title
  - filter labels/placeholders
  - table headers/actions
  - detail labels
  - validation/error/empty-state messages
- English is allowed only for non-UI technical values (ids, enum/code values, API fields).

## Acceptance Checklist (CL-03)
- [ ] Implementation edits stay inside CL-03 allowlist only.
- [ ] List supports `round` + `status` filtering with stable query/pagination behavior.
- [ ] Row detail display is available and bound correctly to selected row data.
- [ ] Error handling follows frozen status mapping with Chinese user messaging.
- [ ] All user-visible text introduced/changed by CL-03 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`

## PE-FE-COM-03 Freeze (提成记录查询页)

### Task / Allowlist
- Task ID: `PE-FE-COM-03`
- Task file: `tasks/postenhancement/frontend/PE-FE-COM-03.md`
- In-scope files for implementation:
  - `frontend/src/modules/commission/pages/CommissionList.vue` (new)
- Out of scope:
  - router wiring changes
  - other module pages/components
  - backend/schema/migration changes

### List Filter Contract (`agent` / `case` / `status` / `date`)
- Commission record list must support filtering by:
  - `agent` (代理人)
  - `case` (案件)
  - `status` (状态)
  - `date` (日期范围)
- Query behavior:
  - filter inputs must map to backend-compatible query keys without alias drift.
  - filter submit triggers list refetch.
  - filter changes reset `page` to `1`.
  - current filters must be preserved during pagination navigation.

### Pagination + Column Contract
- Pagination contract:
  - use backend pagination shape (`items`, `page`, `page_size`, `total`).
  - page and page size changes must trigger refetch with current filter state.
- Column contract:
  - table must expose stable, user-readable columns for commission records, including:
    - record identity/context (record no/id or equivalent)
    - agent
    - case
    - status
    - date/time field used for query
    - amount/summary field as applicable
  - unknown or nullable values must degrade safely (no runtime crash; display fallback text in Chinese).

### Error Mapping Contract
- Use normalized frontend API error flow and Chinese user-facing feedback.
- Status/error mapping contract:
  - `400`: business validation/filter message (Chinese).
  - `401/403`: auth/permission-denied message (Chinese).
  - `404`: target/scope-not-found message when backend returns not found (Chinese).
  - `422`: query validation message (Chinese), prioritize field hints when available.
  - unknown/network errors: generic Chinese failure message.
- Error display must not expose raw backend English internals to end users.

### Simplified Chinese UI Text (Iron Rule)
- All user-visible text introduced/updated in COM-03 scope must be Simplified Chinese:
  - page title
  - filter labels/placeholders
  - column headers
  - button labels
  - validation/error/empty-state messages
- English is allowed only for non-UI technical values (ids, enum/code values, API fields).

## Acceptance Checklist (COM-03)
- [ ] Implementation edits stay inside COM-03 allowlist only.
- [ ] List supports `agent`/`case`/`status`/`date` filters with stable query behavior.
- [ ] Pagination and column rendering follow frozen list contract.
- [ ] Error mapping follows frozen status semantics with Chinese user messaging.
- [ ] All user-visible text introduced/changed by COM-03 is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`
