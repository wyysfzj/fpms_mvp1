# BATCH-A-DEPENDENT-UNHAPPY-P0P1-01 Readiness Gate

## 1. Batch Scope

| Testcase | Topic | Priority | Category | Upstream | Downstream |
| --- | --- | --- | --- | --- | --- |
| TC-A-012 | A2 batch filing validation | P0 | Unhappy, Boundary | TC-A-011 backend batch filing | independent |
| TC-A-016 | A4 fee draft invalid data | P1 | Unhappy, Boundary | TC-A-015 apply fee draft | TC-A-018/020 data quality |
| TC-A-018 | A5 pay-list validation | P1 | Unhappy | TC-A-017 pay-list/payment | finance audit |
| TC-A-020 | A6 bill invalid combinations | P1 | Unhappy | TC-A-019 bill generation | payment offset |
| TC-A-022 | A7 payment/offset invalid data | P1 | Unhappy, Boundary | TC-A-021 payment/offset | commission receipt state |
| TC-A-024 | A8 commission wait-pay threshold | P1 | Boundary | TC-A-023 commission generation | settlement |

This readiness task does not close any testcase. It determines which backend/product/test blockers must be drained before automation landing.

## 2. Capability Matrix

| Testcase | Backend endpoints | Service functions | Current capability | Response/error stability | Readiness |
| --- | --- | --- | --- | --- | --- |
| TC-A-012 | `POST /cases/batch-filing/submit` | `execute_batch_filing` | empty selection and submitted-date-before-receive-date guards already exist | `CASE_BATCH_FILING_SELECTION_REQUIRED`, `CASE_BATCH_FILING_SUBMITTED_DATE_INVALID` stable | ready for automation |
| TC-A-016 | fee draft/item CRUD | `add_fee_item`, `update_fee_item`, fee item delete path | generic CRUD exists, but fee code/name/type invalid inputs are not expressible through current API | existing errors cover rate/currency/locked states only | blocked by product/backend contract |
| TC-A-018 | pay-list and gov-payment endpoints | annuity pay-list and gov-payment services | happy pay-list/payment exists; stale planned-date warning and paid-row privileged edit are not implemented | current errors cover state/scope/duplicate payment, not the full testcase | blocked by product contract / deferred audit API |
| TC-A-020 | `POST /bills/from-drafts`, manual bill | `generate_bill_from_drafts`, manual bill creation | cross-client, currency mismatch, empty item, and negative bill validations exist | stable bill errors already present | ready after backend unhappy test seal |
| TC-A-022 | `POST /payments`, `POST /offsets`, receipt queries | `process_payment`, `create_offset` | amount and offset guards exist; duplicate client/pay number and future date guard are missing | offset errors stable; payment duplicate/date errors missing | blocked by focused backend task |
| TC-A-024 | commission rule/list and billing receipt recompute | `apply_commission_for_bill`, `recompute_commission_settleable` | wait-pay threshold and force-settle logic exists | commission query includes settleable fields | ready after backend readiness evidence |

## 3. Backend Rule / Side Effect Matrix

### TC-A-012

- Required: reject empty selected cases, reject `submitted_date < recv_date`, allow `submitted_date == recv_date`.
- Current support: implemented in `backend/app/modules/cases/service.py`.
- Missing behavior: no backend gap identified.
- Proposed automation task: A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01.

### TC-A-016

- Required: block empty details, empty currency, blank fee code/name, negative quantity/amount, and fee type mismatch; support amount-zero warning / recalculation semantics.
- Current support: generic rate-based item API only accepts `rate_id`, `quantity`, `unit_price`, `remark`.
- Missing behavior: product/API contract does not define how to express blank fee code/name or fee type mismatch in a rate-driven API.
- Proposed blocker tasks: PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01, then BE-A-APPLY-FEE-ITEM-VALIDATION-01.

### TC-A-018

- Required: stale planned-pay-date warning, no actual pay info before paid status, privileged/audited edit for paid official payment.
- Current support: happy pay-list and gov-payment flow exists.
- Missing behavior: warning/audit/edit contract is not present in backend or UI.
- Proposed blocker task: PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01 before backend/frontend work.

### TC-A-020

- Required: reject mixed clients, mixed currency without FX, empty draft/bill, and negative AR bill.
- Current support: billing service already has stable errors for these branches.
- Missing behavior: no focused unhappy-path readiness test yet.
- Proposed blocker task: BE-A-APPLY-BILL-UNHAPPY-01.

### TC-A-022

- Required: reject negative amount, future pay date, duplicate client/pay number, invalid offsets, over-offsets; recognize prepayment.
- Current support: negative amount, invalid offsets, over-offsets, and receipt allocation mostly exist.
- Missing behavior: duplicate client/pay number and future pay date guards are missing.
- Proposed blocker task: BE-A-PAYMENT-OFFSET-UNHAPPY-01.

### TC-A-024

- Required: wait-pay true stays un-settleable until fully received; force-settle true bypasses.
- Current support: commission recompute already applies paid ratio and force-settle rules.
- Missing behavior: focused readiness evidence and automation handler.
- Proposed blocker task: BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01.

## 4. Test-Maintenance Matrix

| File | Stale pattern | Required update | Task |
| --- | --- | --- | --- |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_batch_submit_handler.py` | expects `handle_tc_a_012` skeleton | update only after TC-A-012 handler lands | A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01 |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_apply_fee_draft_handler.py` | expects `handle_tc_a_016` skeleton | update only after TC-A-016 handler lands | A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01 |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_gov_paylist_handler.py` | expects `handle_tc_a_018` skeleton | update only after TC-A-018 handler lands | A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01 |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_apply_bill_handler.py` | expects `handle_tc_a_020` skeleton | update only after TC-A-020 handler lands | A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01 |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_payment_offset_handler.py` | expects `handle_tc_a_022` skeleton | update only after TC-A-022 handler lands | A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01 |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_commission_handler.py` | expects `handle_tc_a_024` skeleton | update only after TC-A-024 handler lands | A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01 |

## 5. Seed / Config Matrix

| Prerequisite | Status | Impact |
| --- | --- | --- |
| Legal case creation with applicants | present | all arrange paths must include applicants |
| APPLY_FEE drafts/items | present for happy path | required by TC-A-016/018/020 |
| Pay list / official payment records | present for happy path | TC-A-018 product warning/audit remains unclear |
| Bills and bill items | present | TC-A-020/022 can arrange prerequisites |
| Payment lines and offsets | present | TC-A-022 needs duplicate/date guard |
| Commission rules and recompute | present | TC-A-024 can arrange wait-pay/force-settle scenarios |

## 6. State-Machine Reachability Matrix

| Testcase | Prerequisite state | API arrange possible | Blocker |
| --- | --- | --- | --- |
| TC-A-012 | legal NOT_FILED cases | yes | none |
| TC-A-016 | OPEN APPLY_FEE draft with items | yes | invalid fields not expressible |
| TC-A-018 | APPLY_FEE GOV item and pay list | yes | warning/audit semantics unclear |
| TC-A-020 | APPLY_FEE drafts under same/different client/currency | yes | needs focused backend unhappy test |
| TC-A-022 | unsettled bill and payment line | yes | duplicate pay number and future date guard missing |
| TC-A-024 | bill with service fee, commission rule, receipt ratios | yes | needs focused readiness evidence |

## 7. Allowlist Matrix

| Task | Task file path | Allowed files | Serialization |
| --- | --- | --- | --- |
| PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01 | `tasks/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md` | task file, product doc, artifacts | product docs |
| BE-A-APPLY-FEE-ITEM-VALIDATION-01 | `tasks/backend/business_logic/BE-A-APPLY-FEE-ITEM-VALIDATION-01.md` | fees API/service/schema, focused backend test, artifacts | fees module |
| PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01 | `tasks/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md` | task file, product doc, artifacts | product docs |
| BE-A-PAYMENT-OFFSET-UNHAPPY-01 | `tasks/backend/business_logic/BE-A-PAYMENT-OFFSET-UNHAPPY-01.md` | billing API/service/schema, focused backend test, artifacts | billing module |
| BE-A-APPLY-BILL-UNHAPPY-01 | `tasks/backend/business_logic/BE-A-APPLY-BILL-UNHAPPY-01.md` | billing API/service/schema, focused backend test, artifacts | billing module |
| BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01 | `tasks/backend/business_logic/BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01.md` | commission service/API/schema, focused backend test, artifacts | commission module |

## 8. Blocker Drain Manifest

Execution order:

1. PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01
2. BE-A-APPLY-FEE-ITEM-VALIDATION-01
3. PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01
4. BE-A-PAYMENT-OFFSET-UNHAPPY-01
5. BE-A-APPLY-BILL-UNHAPPY-01
6. BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01

The executable manifest is `tasks/batches/BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-BLOCKER-DRAIN.md`.

## 9. Automation Landing Readiness

| Automation task | Testcase | Can start now | Must wait for |
| --- | --- | --- | --- |
| A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01 | TC-A-012 | yes | none |
| A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01 | TC-A-016 | no | product/backend fee invalid blockers |
| A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01 | TC-A-018 | no | product gov pay-list unhappy contract |
| A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01 | TC-A-020 | yes after backend unhappy evidence | BE-A-APPLY-BILL-UNHAPPY-01 |
| A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01 | TC-A-022 | no | BE-A-PAYMENT-OFFSET-UNHAPPY-01 |
| A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01 | TC-A-024 | yes after backend readiness evidence | BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01 |

## 10. Readiness Decision

Readiness Gate result: PASS for blocker discovery and manifest preparation once evidence gate passes.

Batch 3 testcase result: not closed by readiness. TC-A-016 and TC-A-018 must not be automated until their product/backend blockers are resolved.
