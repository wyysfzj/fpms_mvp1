# BATCH-FE-COMPLETENESS-RESIDUAL-GAPS-01-BLOCKER-DRAIN

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Execution Order

### 1. PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01

- Type: product contract
- Task file: `tasks/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md`
- Closure slice: freeze document wizard real-write UX semantics for existing backend batch-create behavior.
- Non-closure: no FE or backend implementation.
- Allowed files:
  - `tasks/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md`
  - `docs/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md`
  - `artifacts/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01/**`
- Verification:
  - `test -f tasks/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md`
  - `test -f docs/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md`
  - `rg -n "批量创建|最终提交|预览|task_rows|fee_rows|attachment_rows|MVP" docs/product/PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01.md`
  - `./scripts/task_validate.sh PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01`

### 2. FE-MENU-ROUTE-DISCOVERABILITY-02

- Type: frontend capability
- Task file: `tasks/frontend/FE-MENU-ROUTE-DISCOVERABILITY-02.md`
- Closure slice: expose already-existing residual routes through menu/list actions without changing backend behavior.
- Non-closure: no new backend capability, no raw-ID selector work, no wizard real-write behavior change.
- Allowed files:
  - `tasks/frontend/FE-MENU-ROUTE-DISCOVERABILITY-02.md`
  - `frontend/src/constants/menu.ts`
  - `frontend/src/constants/perms.ts`
  - `frontend/src/modules/documents/pages/DocumentList.vue`
  - `frontend/src/modules/settings/pages/MasterDataHome.vue`
  - `artifacts/FE-MENU-ROUTE-DISCOVERABILITY-02/**`
- Verification:
  - `cd frontend && npm run typecheck`
  - `cd frontend && npm run build`
  - `./scripts/task_validate.sh FE-MENU-ROUTE-DISCOVERABILITY-02`

## Deferred Blockers

### PRODUCT-COMMISSION-BILL-NO-QUERY-CONTRACT-01

Bill-number commission search requires a durable commission-to-bill linkage contract. Current commission records carry `case_id` but not `bill_id`.

### BE-FE-COMMISSION-QUERY-READINESS-01

Case-number commission search needs backend support for `case_no` filtering before FE can expose a business-friendly query field honestly.

### FE-CASE-RELATED-SELECTORS-01-SPLIT

Raw-ID selector work must be split into smaller tasks. Agent/worker selectors require a role-filtered user source decision and must not be implemented as a generic raw user dropdown without contract.
