# Wave 49 Contract Freeze

## Task Scope
- Wave: `49`
- Role: Architect / Designer
- Frozen tasks:
  - `tasks/postenhancement/frontend/PE-FE-QA-01.md`
- Current execution freeze: `PE-FE-QA-01`
- Freeze focus:
  - unified new-module routing/menu/permission gate
  - no regression of old menu behavior
  - permission codes align existing constants
  - Simplified Chinese UI text rule
- This execution is doc-only; no product code changes.

## Global FE Conventions (Mandatory)
- Enforce atomic allowlist isolation for this task.
- Keep route path and menu route consistency; no dead links.
- Keep permission gating through `requiredPerms` in `MENU_GROUPS`.
- All user-facing text touched in this task must be Simplified Chinese.

## PE-FE-QA-01 Freeze（统一新增模块路由、菜单、权限 gate）

### Task / Allowlist
- Task ID: `PE-FE-QA-01`
- Task file: `tasks/postenhancement/frontend/PE-FE-QA-01.md`
- Dependency: FE-B1~B4 complete
- In-scope files for implementation:
  - `frontend/src/router/index.ts`
  - `frontend/src/constants/menu.ts`
- Out of scope:
  - all module page files
  - auth store / permission constants file changes
  - backend/schema/migration/test changes
  - unrelated UI refactors

### Unified New-Module Routing Contract
- `frontend/src/router/index.ts` must include routable entries for B1~B4 new module pages used by current page navigation:
  - `AnnuityTaskList.vue` -> `/annuity/tasks`
  - `PayList.vue` -> `/annuity/pay-lists`
  - `GovPaymentCreate.vue` -> `/annuity/gov-payments/new`
  - `DunningList.vue` -> `/collections/dunning`
  - `DunningCreate.vue` -> `/collections/dunning/new`
  - `DunningDetail.vue` -> `/collections/dunning/:id`
  - `CommissionList.vue` -> `/commission`
  - `CommissionRuleList.vue` -> `/commission/rules`
  - `CommissionSettlement.vue` -> `/commission/settlements`
  - `ConsultingCaseCreate.vue` -> `/consulting/cases/new`
  - `ConsultingFeeDraftCreate.vue` -> `/consulting/fee-drafts/new`
  - `ConsultingProfitability.vue` -> `/consulting/profitability`
  - `ExpenseList.vue` -> `/expenses`
  - `ExpenseCreate.vue` -> `/expenses/new`
- Route records added in this task must use unique route names and deterministic component mapping.

### Old Menu Non-Regression Contract
- Existing legacy menu entries must keep behavior compatibility:
  - `dashboard` -> `/dashboard`
  - `clients` -> `/clients`
  - `cases` -> `/cases`
  - `tasks` -> `/tasks`
  - `fees` -> `/fees/drafts`
  - `payments` -> `/billing/payments`
  - `settings` -> `/system/params`
  - `task_templates` -> `/system/task-templates`
  - `doc_templates` -> `/system/doc-templates`
- Do not delete/rename legacy menu keys above.
- If route path migration is needed, preserve old path reachability with alias/redirect to avoid breaking existing entry points.

### Unified Menu + Permission Gate Contract
- `MENU_GROUPS` remains the single source of truth for sidebar grouping and display order.
- Any new menu item added in this task must define `requiredPerms` with imported `Perms.*` constants only.
- Do not hardcode literal permission strings in `menu.ts`.
- Existing menu permission gates must not be weakened or removed.
- This atomic task does not modify `frontend/src/constants/perms.ts`; if a dedicated new-module permission constant does not exist, prefer route integration first and avoid introducing mismatched literal permissions.

### Simplified Chinese UI Text Contract
- `menu.ts` is user-facing UI text scope in this task.
- All touched/new group labels and menu labels must be Simplified Chinese.
- Mixed Chinese-English labels touched by this task must be normalized to Simplified Chinese within task scope.
- English is allowed only for technical values (ids, enum/code values, API field names).

## Acceptance Checklist (PE-FE-QA-01)
- [ ] Implementation edits stay strictly inside QA-01 allowlist.
- [ ] New-module routes are wired and match page navigation paths listed in this freeze.
- [ ] Existing legacy menu keys/routes keep backward-compatible behavior (no dead links/regression).
- [ ] Menu permission gates use existing `Perms.*` constants only and do not weaken existing guards.
- [ ] All touched user-visible menu text is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint && npm run typecheck`
