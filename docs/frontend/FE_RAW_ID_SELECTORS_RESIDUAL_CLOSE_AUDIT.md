# FE Raw-ID Selectors Residual Close Audit

## Scope

This audit covers the recent FE completeness residual work after route discoverability, commission case-number search, billing selectors, and task case selector remediation.

## Fixed

| Capability | Task | Evidence |
| --- | --- | --- |
| Document wizard real-write copy and action semantics | `FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01` | `artifacts/FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01/` |
| Commission search by business case number | `BE-FE-COMMISSION-QUERY-READINESS-01` and `FE-COMMISSION-CASE-NO-FILTER-01` | `artifacts/BE-FE-COMMISSION-QUERY-READINESS-01/`, `artifacts/FE-COMMISSION-CASE-NO-FILTER-01/` |
| Billing manual bill client/case selectors and payment bill/client selectors | `FE-BILLING-RAW-ID-SELECTORS-01` | `artifacts/FE-BILLING-RAW-ID-SELECTORS-01/` |
| Task creation case selector | `FE-TASK-CASE-SELECTOR-01` | `artifacts/FE-TASK-CASE-SELECTOR-01/` |
| Residual route discoverability | `FE-MENU-ROUTE-DISCOVERABILITY-02` | `artifacts/FE-MENU-ROUTE-DISCOVERABILITY-02/` |

## Residual

| Area | Current blocker | Next task |
| --- | --- | --- |
| Document edit and wizard reply-source selectors | Existing APIs can support business selectors, but this needs a focused document-only slice. | `FE-DOCUMENT-CASE-SELECTORS-01` |
| PayList client/case selectors | Existing APIs can support client/case selectors; manual fee-item selector is excluded. | `FE-PAYLIST-CLIENT-CASE-SELECTORS-01` |
| Agent/worker/assignee selectors | Product must decide valid user source: all users, active users, role-filtered users, or endpoint-specific eligibility. | `PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01` |
| PayList manual fee-item selector | No stable case/pay-list-scoped eligible fee-item source is confirmed. | `PRODUCT-FE-PAYLIST-MANUAL-FEE-ITEM-SELECTOR-CONTRACT-01` |
| Commission bill-number search | Current commission records do not expose durable bill linkage. | `PRODUCT-COMMISSION-BILL-NO-QUERY-CONTRACT-01` |

## Recommended Order

1. `FE-DOCUMENT-CASE-SELECTORS-01`
2. `FE-PAYLIST-CLIENT-CASE-SELECTORS-01`
3. `PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01`
4. `PRODUCT-FE-PAYLIST-MANUAL-FEE-ITEM-SELECTOR-CONTRACT-01`
5. `PRODUCT-COMMISSION-BILL-NO-QUERY-CONTRACT-01`

## GO / NO-GO

GO for continuing safe FE-only selector remediation with document and PayList client/case selectors.

NO-GO for replacing agent/worker selectors or manual fee-item selectors until product/backend source contracts are frozen.

## Verification

Final frontend verification for this close audit:

- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`

Recent task gates to retain as acceptance evidence:

- `FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01`
- `BE-FE-COMMISSION-QUERY-READINESS-01`
- `FE-COMMISSION-CASE-NO-FILTER-01`
- `FE-BILLING-RAW-ID-SELECTORS-01`
- `FE-TASK-CASE-SELECTOR-01`
