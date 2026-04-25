# FE Completeness Audit

## 1. Scope And Method

This audit reviews frontend application completeness, not demo stability. The
criterion is whether a normal business user can enter from the visible product
navigation, select business objects without raw IDs or direct API calls, trigger
real backend behavior, and see the resulting business state.

Sources checked:

- frontend routes, menus, API wrappers, and module pages
- backend API modules for capability and permission alignment
- prior A/B wave evidence and manual demo findings

This document is source-based. Runtime browser verification belongs to the
remediation close audit.

## 2. Executive Summary

The frontend already has broad module coverage, but several important backend
capabilities are not exposed as complete user flows. The most serious gaps are
in the A-wave finance chain: real application fee generation, official pay list
creation, official payment registration from pay-list items, payment creation,
bill direction visibility, and commission settleability visibility.

The remediation should not be implemented as one broad frontend sweep. It should
use readiness-first execution, split product/backend ambiguity into blockers,
and land one frontend capability per atomic task.

## 3. P0 Findings

| Gap ID | Area | Finding | Evidence Source | Recommended Task |
| --- | --- | --- | --- | --- |
| FE-COMP-001 | Fees | Real `APPLY_FEE` generation has a backend endpoint but no clear user-facing frontend action. | `backend/app/modules/fees/api.py`, `frontend/src/modules/fees/pages/FeeDraftCreate.vue` | FE-FEE-APPLY-FEE-GENERATE-01 |
| FE-COMP-002 | Cases/Fees | Case fee tab routes users to generic draft creation, which can create zero-amount generic drafts instead of real application-fee drafts. | `frontend/src/modules/cases/components/CaseFeesTab.vue` | FE-FEE-APPLY-FEE-GENERATE-01 |
| FE-COMP-003 | PayList | Pay list creation from GOV fee items has an API wrapper but no complete UI path. | `frontend/src/api/govPayments.ts`, `frontend/src/modules/annuity/pages/PayList.vue` | FE-PAYLIST-FROM-FEE-ITEMS-01 |
| FE-COMP-004 | PayList | Pay-list detail route exists, but the list page does not make detail navigation discoverable enough for normal operation. | `frontend/src/router/index.ts`, `frontend/src/modules/annuity/pages/PayList.vue` | FE-PAYLIST-DETAIL-ENTRY-01 |
| FE-COMP-005 | GovPayment | Pay-list detail navigation to official payment registration lacks stable fee-item context. | `frontend/src/modules/annuity/pages/PayListDetail.vue`, `frontend/src/modules/annuity/pages/GovPaymentCreate.vue` | FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01 |
| FE-COMP-006 | Payments | Payment list does not expose an obvious new-payment entry despite a payment-create route existing. | `frontend/src/router/index.ts`, `frontend/src/modules/billing/pages/PaymentList.vue` | FE-PAYMENT-CREATE-ENTRY-01 |
| FE-COMP-007 | Payments | Payment creation remains backend-oriented; business fields such as pay number, client, bill, and currency need clearer UI semantics. | `frontend/src/modules/billing/pages/PaymentCreate.vue` | FE-PAYMENT-CREATE-ENTRY-01 |
| FE-COMP-008 | Bills | Bill direction is modeled and returned by backend/types, but list/detail visibility is incomplete. | `backend/app/modules/billing/schemas.py`, `frontend/src/api/billing.types.ts`, `frontend/src/modules/billing/pages/BillDetail.vue` | FE-BILL-DIRECTION-VISIBILITY-01 |
| FE-COMP-009 | Commission | Commission records do not expose `wait_pay` and `force_settle`, even though backend/API types include them. | `backend/app/modules/commission/api.py`, `frontend/src/api/commission.types.ts`, `frontend/src/modules/commission/pages/CommissionList.vue` | FE-COMMISSION-SETTLEABILITY-VISIBILITY-01 |
| FE-COMP-010 | Permissions | PayList and Commission menu permissions appear misaligned with backend `require_perm` values. | `frontend/src/constants/menu.ts`, backend API modules | FE-MENU-PERMISSION-ALIGNMENT-01 |

## 4. P1 Findings

| Gap ID | Area | Finding | Recommended Handling |
| --- | --- | --- | --- |
| FE-COMP-011 | Case forms | Some form fields still require raw IDs for address, agent, and related entities. | FE-CASE-RELATED-SELECTORS-01 |
| FE-COMP-012 | Case forms | Priority and inventor editing is not discoverable enough for full case walkthroughs. | FE-CASE-FULL-FIELDS-USABILITY-01 |
| FE-COMP-013 | Billing offsets | Offset creation UI should expose all business fields that backend expects, including effective offset date if supported. | FE-PAYMENT-OFFSET-USABILITY-01 |
| FE-COMP-014 | Commission search | Commission search is not business-friendly enough if users only know case number or bill number. | Backend readiness first if API does not support it |
| FE-COMP-015 | Routes | Some routes exist but are not reachable from menu/list actions. | FE-MENU-ROUTE-DISCOVERABILITY-01 |

## 5. P2 Findings

| Gap ID | Area | Finding | Recommended Handling |
| --- | --- | --- | --- |
| FE-COMP-016 | Documents | Document wizard contains MVP limitations around real task/fee write behavior. | Product contract before implementation |
| FE-COMP-017 | Documents | Dispatch/envelope flows include limited audit/logging behavior. | Product contract before implementation |
| FE-COMP-018 | Docs | Some module docs still describe future/MVP gaps that may now be partially implemented. | Documentation maintenance |
| FE-COMP-019 | Error visibility | Some pages silently ignore secondary fetch failures. | Focused UX hardening tasks |

## 6. Remediation Batch Groups

### FE-COMP-FINANCE-HAPPY-PATH-01

- FE-FEE-APPLY-FEE-GENERATE-01
- FE-PAYLIST-FROM-FEE-ITEMS-01
- FE-PAYLIST-DETAIL-ENTRY-01
- FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01
- FE-BILL-DIRECTION-VISIBILITY-01
- FE-PAYMENT-CREATE-ENTRY-01

### FE-COMP-COMMISSION-VISIBILITY-01

- FE-COMMISSION-SETTLEABILITY-VISIBILITY-01
- Backend blocker if case-no or bill-no query is not available.

### FE-COMP-PERMISSION-MENU-ALIGNMENT-01

- FE-MENU-PERMISSION-ALIGNMENT-01

### FE-COMP-CASE-FORM-USABILITY-01

- FE-CASE-RELATED-SELECTORS-01
- FE-CASE-FULL-FIELDS-USABILITY-01

### FE-COMP-DOCUMENT-TASK-LINKAGE-01

- PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01
- Backend/frontend follow-ups after product contract.

## 7. Execution Guidance

Use a readiness gate before implementation. Do not implement fake UI flows for
backend behavior that does not exist. Do not use direct URL knowledge as a
substitute for discoverable navigation. Each remediation task must own exactly
one capability closure and must record evidence independently.
