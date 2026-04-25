# FE Completeness Remediation Readiness

## 1. Batch Scope

Readiness source: `docs/frontend/FE_COMPLETENESS_AUDIT.md`.

Target capabilities:

- real application fee draft generation
- official pay-list creation from GOV fee items
- pay-list detail navigation
- official payment registration with fee-item context
- AR/AP bill direction visibility
- payment creation entry and clearer payment labels
- commission wait-pay / force-settle visibility
- menu permission alignment

## 2. Capability Matrix

| Gap ID | Module | Capability | Backend Endpoint | FE Wrapper | Page | Menu/List Entry | Permission Alignment | Product Ambiguity | Backend Blocker | FE Task | Priority | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FE-COMP-001 | Fees | Generate real `APPLY_FEE` draft | yes: `POST /fees/drafts/apply-fee/generate` | partial/missing dedicated wrapper | partial | no | yes | no | no | FE-FEE-APPLY-FEE-GENERATE-01 | P0 | ready |
| FE-COMP-002 | Cases/Fees | Case tab enters real fee generation | yes | partial | partial | partial | yes | no | no | FE-FEE-APPLY-FEE-GENERATE-01 | P0 | ready |
| FE-COMP-003 | PayList | Create pay list from GOV fee items | yes: `POST /pay-lists/from-fee-items` | yes | partial | no | no | no | no | FE-PAYLIST-FROM-FEE-ITEMS-01 | P0 | ready |
| FE-COMP-004 | PayList | Navigate from list to detail | yes: `GET /pay-lists/{id}` | yes | yes | partial | no | no | no | FE-PAYLIST-DETAIL-ENTRY-01 | P0 | ready |
| FE-COMP-005 | GovPayment | Register payment from pay-list item | yes: `POST /gov-payments` | yes | partial | partial | no | no | unclear context shape | FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01 | P0 | ready after detail inspection |
| FE-COMP-006 | Payments | Visible new payment entry | yes: `POST /payments` | yes | yes | no | yes | no | no | FE-PAYMENT-CREATE-ENTRY-01 | P0 | ready |
| FE-COMP-007 | Payments | Business-friendly payment labels | yes | yes | partial | partial | yes | no | no | FE-PAYMENT-CREATE-ENTRY-01 | P0 | ready |
| FE-COMP-008 | Billing | Show bill direction | yes | yes | partial | partial | yes | no | no | FE-BILL-DIRECTION-VISIBILITY-01 | P0 | ready |
| FE-COMP-009 | Commission | Show wait-pay / force-settle | yes | yes | partial | partial | no | no | no | FE-COMMISSION-SETTLEABILITY-VISIBILITY-01 | P0 | ready |
| FE-COMP-010 | Navigation | Align PayList/Commission menu permissions | yes | n/a | n/a | no | no | no | no | FE-MENU-PERMISSION-ALIGNMENT-01 | P0 | ready |
| FE-COMP-011 | Cases | Replace raw ID fields with selectors | yes/unclear by field | mixed | partial | partial | yes | possible | possible | FE-CASE-RELATED-SELECTORS-01 | P1 | defer |
| FE-COMP-016 | Documents | Wizard real task/fee write behavior | backend partially supports preview/write paths | partial | partial | partial | yes | yes | possible | PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01 | P2 | blocker/product |

## 3. Route / Menu Matrix

| Route | Page | Menu/List Reachability | Readiness Decision |
| --- | --- | --- | --- |
| `/fees/drafts/new` | generic fee draft create | reachable from fee list/case tab but not correct for `APPLY_FEE` | replace or branch from case tab into real generation |
| `/fee-management/pay-lists` | pay-list list | menu exists | permission alignment required |
| `/fee-management/pay-lists/:id` | pay-list detail | route exists; list detail action needs strengthening | implement detail entry |
| `/fee-management/gov-payments/new` | payment registration | route exists; needs fee-item context from pay-list detail | implement item-scoped navigation |
| `/billing/payments/new` | payment create | route exists; list lacks visible entry | add entry |
| `/commission` | commission records | menu exists; permission mismatch | align permission and improve columns |
| `/documents/wizard` | document wizard | route exists; product semantics unclear for real writes | product contract before remediation |
| `/system/letterheads` | letterhead list | route exists; menu absent | defer to P2 navigation sweep |

## 4. Endpoint / Wrapper / Page Matrix

| Backend Endpoint | FE Wrapper | Page Usage | Decision |
| --- | --- | --- | --- |
| `POST /fees/drafts/apply-fee/generate` | missing or not exposed as dedicated action | not used by `FeeDraftCreate` | add wrapper/action in FE-FEE-APPLY-FEE-GENERATE-01 |
| `POST /pay-lists/from-fee-items` | `createPayListFromFeeItems` | wrapper exists; page use incomplete | use in FE-PAYLIST-FROM-FEE-ITEMS-01 |
| `GET /pay-lists/{id}` | `getPayListDetail` | detail route exists | add discoverable entry |
| `POST /gov-payments` | `registerGovPayment` | create page exists | pass pay-list item context |
| `POST /payments` | `createPayment` | create page exists | add list entry and label cleanup |
| `GET /commission` | `listCommissions` | page exists | add missing visibility columns |

## 5. Raw-ID Usability Matrix

| Page | Raw-ID Risk | This Batch Decision |
| --- | --- | --- |
| CaseCreate / CaseEdit | client address, agent, related ids | defer to FE-CASE-RELATED-SELECTORS-01 |
| PaymentCreate | bill id and transaction reference semantics | improve labels/entry only in this batch |
| BillCreate | client/case direct ids | defer to separate selector task |
| PayListCreate | client/manual item context | use fee-item-driven path first |
| CommissionList | case id search | show existing fields; backend query extension only if needed |

## 6. Product / Backend Blocker Matrix

| Blocker | Type | Decision |
| --- | --- | --- |
| Document wizard real task/fee write behavior | product/backend | defer to PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01 |
| Case raw-ID selector coverage | FE usability / possible backend lookup | defer to FE-CASE-RELATED-SELECTORS-01 |
| Commission case-no/bill-no search | backend readiness if API lacks filters | do not fake; only add if current API supports it |

## 7. Allowlist Matrix

| Task ID | Closure Slice | Allowed Files | Shared File Note | Dependencies |
| --- | --- | --- | --- | --- |
| FE-FEE-APPLY-FEE-GENERATE-01 | Real APPLY_FEE generation UI path | task file, fees API/types, FeeDraftCreate/Detail, CaseFeesTab, artifacts | fees API serialized | audit/readiness |
| FE-PAYLIST-FROM-FEE-ITEMS-01 | Create PayList from GOV FeeItems | task file, govPayments API/types, PayList/PayListCreate, artifacts | govPayments API serialized | fee generation readiness |
| FE-PAYLIST-DETAIL-ENTRY-01 | Discoverable PayList detail entry | task file, PayList, PayListDetail, artifacts | PayList page serialized | none |
| FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01 | Register GovPayment from specific item | task file, PayListDetail, GovPaymentCreate, artifacts | serialized after detail entry | pay-list detail |
| FE-BILL-DIRECTION-VISIBILITY-01 | Bill direction visible | task file, BillList, BillDetail, artifacts | billing pages only | none |
| FE-PAYMENT-CREATE-ENTRY-01 | Visible payment creation entry and labels | task file, PaymentList, PaymentCreate, artifacts | billing pages only | none |
| FE-COMMISSION-SETTLEABILITY-VISIBILITY-01 | Commission wait-pay/force-settle visible | task file, commission API/types, CommissionList, artifacts | commission API serialized | none |
| FE-MENU-PERMISSION-ALIGNMENT-01 | Menu permissions aligned | task file, menu/perms constants, artifacts | menu serialized | after capability tasks |

## 8. Automation / Smoke Readiness

Frontend typecheck and build are available through `frontend/package.json`.
There are no discovered frontend unit test files in this repo snapshot, so
targeted verification will rely on typecheck/build plus focused source checks.

Runtime Playwright smoke should be performed at close audit if backend/frontend
services are available. Offline source-only PASS is not sufficient for runtime
walkthrough claims.
