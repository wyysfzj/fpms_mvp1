# BATCH-A-HAPPY-MAIN-CHAIN-P0-01 Readiness Gate

## 1. Batch Scope

| Testcase | Topic | Priority | Category | Upstream | Downstream |
| --- | --- | --- | --- | --- | --- |
| TC-A-011 | A2 batch filing succeeds | P0 | Happy | legal NOT_FILED domestic cases | TC-A-013 |
| TC-A-013 | A3 application-fee deadline task generated | P0 | Happy | submitted case and APPLY_FEE_LIMIT template/trigger | TC-A-015 |
| TC-A-015 | A4 application-fee draft generated | P0 | Happy | domestic invention case, claim count, fee reduction, fee rates | TC-A-017, TC-A-019 |
| TC-A-017 | A5 official fee pay list and payment | P0 | Happy | APPLY_FEE draft with GOV item | later fee visibility |
| TC-A-019 | A6 application-fee bill generated | P0 | Happy | one or two APPLY_FEE drafts under one client | TC-A-021, TC-A-023 |
| TC-A-021 | A7 customer payment and offset | P0 | Happy | unsettled bill | payment visibility |
| TC-A-023 | A8 commission generated and settleable entry visible | P0 | Happy | application-fee bill with SERVICE item and commission rule | Batch 3 settlement/unhappy work |

The skeleton data confirms these seven testcase IDs are in the A wave and P0 smoke set. The readiness gate does not close any testcase; it only determines whether backend, product, seed/config, test-maintenance, and environment prerequisites are ready.

## 2. Capability Matrix

| Testcase | Backend endpoints | Service functions | Model/table dependencies | Endpoint exists | Service behavior exists | Response stable | Error semantics stable | Frontend/API path observed | Readiness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-A-011 | `GET /cases/batch-filing/candidates`, `POST /cases/batch-filing/submit` | `execute_batch_filing` | `Case`, `Document`, `Task`, `TaskTemplate`, `TaskLog` | yes | implemented by BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02 but not revalidated PASS | yes: preserved counts/ids plus optional side-effect ids | yes for batch validation codes | `frontend/src/api/cases.ts` | blocked by stale backend tests |
| TC-A-013 | `GET /tasks`, `GET /tasks/{id}/logs` | task list/log services plus batch-created APPLY_FEE_LIMIT task | `Task`, `TaskTemplate`, `TaskLog` | yes | partial: task is created; reminders and assignment from batch path need verification | unclear for full skeleton fields | mostly stable; creation semantics need test | `frontend/src/modules/tasks/**` | blocked by TC-A-011 test maintenance and task-field verification |
| TC-A-015 | `/fees/drafts`, `/fees/drafts/{id}/items`, `/fees/rates` | generic fee draft/item/rate services | `FeeDraft`, `FeeItem`, `FeeRate`, `Case` | yes | missing/unclear: no stable APPLY_FEE generation endpoint from claim count and fee reduction discovered | unclear | unclear | `frontend/src/modules/fees/**` | blocked by product contract and backend rule/API task |
| TC-A-017 | `/pay-lists/from-fee-items`, `/pay-lists`, `/pay-lists/{id}/export`, `/pay-lists/{id}/mark-paid`, `/gov-payments` | annuity pay-list and official-payment services | `PayList`, `PayListItem`, `GovPayment`, `FeeItem`, `FeeDraft` | yes | likely present once GOV fee item exists | likely stable; needs targeted readiness test | stable in annuity service errors, not yet mapped to TC-A-017 | `frontend/src/api/govPayments.ts` | waits for TC-A-015, then targeted readiness |
| TC-A-019 | `POST /bills/from-drafts`, bill list/detail | `generate_bill_from_drafts` | `Bill`, `BillItem`, `FeeDraft`, `FeeItem`, `CaseReceipt` | yes | likely present | likely stable | stable enough, needs APPLY_FEE draft fixture | `frontend/src/api/billing.ts` | waits for TC-A-015, then targeted readiness |
| TC-A-021 | `POST /payments`, `POST /offsets`, payment/offset lists | `process_payment`, `create_offset` | `Payment`, `PaymentLine`, `Offset`, `Bill`, `CaseReceipt` | yes | likely present | likely stable | over-offset is out of scope; happy offset needs readiness test | `frontend/src/api/billing.ts` | waits for TC-A-019 |
| TC-A-023 | `/commission`, `/commission/rules`, settlement report/query paths | `apply_commission_for_bill`, `recompute_commission_settleable` | `Commission`, `CommissionRule`, `BillItem`, agent split/case agent data | yes | likely present through billing hook | likely stable | unclear seed/config for NORMAL rule and split | `frontend/src/api/commission.ts` | waits for TC-A-019 and commission arrange readiness |

## 3. Backend Rule / Side Effect Matrix

### TC-A-011

- Required side effects: NOT_FILED to WAITING_RECEIPT, submitted date, invention exam request, submission-list document registration, APPLY_FEE_LIMIT trigger.
- Current support: BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02 added API wiring, one Document per case, idempotent APPLY_FEE_LIMIT creation, and backward-compatible response fields.
- Missing behavior: no backend logic gap identified, but old batch filing tests fail before target semantics because their case setup lacks applicants.
- Evidence source: `artifacts/BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02/summary.md`.
- Proposed blocker task: BE-A-BATCH-FILING-TEST-MAINT-01.

### TC-A-013

- Required side effects: APPLY_FEE_LIMIT task has base date, deadline, internal deadline, reminders, worker, supervisor, OPEN status, and CREATE-style TaskLog.
- Current support: task model and task API support these fields; batch filing currently creates base/due/internal dates and TaskLog with auto-create action.
- Missing behavior: batch-created tasks do not yet have a focused test for reminder fields, default worker/supervisor assignment, and full skeleton field semantics.
- Evidence source: `backend/app/modules/cases/service.py`, `backend/app/modules/tasks/models.py`, `backend/tests/test_task_generation.py`.
- Proposed blocker task: BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01.

### TC-A-015

- Required side effects: one APPLY_FEE draft, FeeItems, fee reduction, excess claim fee beyond ten claims, service fee discount, stable totals.
- Current support: generic FeeDraft/FeeItem/FeeRate CRUD and fee calculation helpers exist.
- Missing behavior: a stable APPLY_FEE generation endpoint/service from case + fee rates was not confirmed. Existing generation code is specific to other flows or generic/manual CRUD.
- Evidence source: `backend/app/modules/fees/api.py`, `backend/app/modules/fees/service.py`, fee-related backend tests.
- Proposed blocker tasks: PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01, then BE-A-APPLY-FEE-DRAFT-RULE-01.

### TC-A-017

- Required side effects: official pay list from GOV fee item, planned date, export/list, GovPayment, PAID status, paid amount visibility.
- Current support: annuity module exposes pay-list and GovPayment endpoints even though the API path is not named by A wave.
- Missing behavior: TC-A-017 cannot be validated until TC-A-015 can produce a GOV fee item. A targeted readiness test should confirm APPLY_FEE items are accepted by existing pay-list services.
- Evidence source: `backend/app/modules/annuity/api.py`, `backend/app/modules/annuity/service.py`, `frontend/src/api/govPayments.ts`.
- Proposed blocker task: BE-A-GOV-PAYLIST-PAYMENT-READINESS-01.

### TC-A-019

- Required side effects: bill from APPLY_FEE draft, BillItem links FeeDraft/FeeItem, totals/balance/status UNSETTLED.
- Current support: `POST /bills/from-drafts` and `generate_bill_from_drafts` exist.
- Missing behavior: readiness still depends on TC-A-015 producing suitable APPLY_FEE drafts and items. A targeted readiness test should lock the A-wave fixture shape.
- Evidence source: `backend/app/modules/billing/api.py`, `backend/app/modules/billing/service.py`.
- Proposed blocker task: BE-A-APPLY-BILL-READINESS-01.

### TC-A-021

- Required side effects: payment, payment line, offset, bill balance/status, CaseReceipt received and arrears.
- Current support: billing module has payment and offset endpoints and services.
- Missing behavior: needs targeted happy-flow readiness test after bill generation to prevent automation discovering a hidden CaseReceipt or status mismatch late.
- Evidence source: `backend/app/modules/billing/api.py`, `backend/app/modules/billing/service.py`.
- Proposed blocker task: BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01.

### TC-A-023

- Required side effects: commission generated/updated per agent, base fee from service fee, S1/S2 amounts, 70/30 split, wait-pay/force-settle initial values, settleable entry query.
- Current support: commission API, rule API, billing hook, and commission service exist.
- Missing behavior: NORMAL rule seed/config and A-wave main/co-agent arrange path need focused confirmation.
- Evidence source: `backend/app/modules/commission/api.py`, `backend/app/modules/commission/service.py`, billing commission hook.
- Proposed blocker task: BE-A-COMMISSION-RULE-SEED-READINESS-01.

## 4. Test-Maintenance Matrix

| File | Stale pattern | Cause | Required update | Proposed task | Allowlist required |
| --- | --- | --- | --- | --- | --- |
| `backend/tests/test_case_batch_filing_action.py` | creates cases without applicants | Batch 1 applicant rule now enforces `CASE_APPLICANT_REQUIRED` | add valid applicant prerequisites only | BE-A-BATCH-FILING-TEST-MAINT-01 | yes |
| `backend/tests/test_case_batch_filing_query.py` | creates cases without applicants | same applicant prerequisite | add valid applicant prerequisites only | BE-A-BATCH-FILING-TEST-MAINT-01 | yes |
| `FPMS_Automation_Skeleton_Pack/pytest_python/tests/*` | possible future skeleton-state assertions around `handle_tc_a_011/013/015/017/019/021/023` | future handler implementation will make old boundary assertions stale | scan and allowlist per automation task | each A-AUTO-PY task | yes, per exact stale file |

No Readiness Gate change may modify these tests. The blocker drain manifest defines the backend test-maintenance task separately.

## 5. Seed / Config Matrix

| Prerequisite | Status | Source checked | Proposed task if missing |
| --- | --- | --- | --- |
| valid clients/applicants | present | skeleton seeds and backend seed/dev tests | none; automation/test fixtures must include applicants |
| APPLY_FEE_LIMIT template | present or auto-created minimally by batch filing service | `backend/app/modules/cases/service.py` | BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01 for full field semantics |
| document template / binary renderer | not required for current minimal side-effect | BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02 summary | none unless product requires attachment rendering |
| APPLY_FEE fee rates | unclear for TC-A-015 generation | `backend/app/modules/fees/service.py`, tests | PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01 and BE-A-APPLY-FEE-DRAFT-RULE-01 |
| finance user / permissions | admin path likely enough; dedicated Finance seed unclear | auth/permission tests and frontend usage | record in BE-A-GOV-PAYLIST-PAYMENT-READINESS-01 |
| commission NORMAL rule | API exists; default seed unclear | `backend/app/modules/commission/api.py`, service | BE-A-COMMISSION-RULE-SEED-READINESS-01 |
| main/co-agent split | model exists; arrange path must be confirmed | cases models/service and commission service | BE-A-COMMISSION-RULE-SEED-READINESS-01 |

## 6. State-Machine Reachability Matrix

| Testcase | Prerequisite state | Public API arrange path | Blockers | Fixture acceptable for backend task |
| --- | --- | --- | --- | --- |
| TC-A-011 | three legal NOT_FILED domestic cases | case create API with valid applicants and legal date/status payloads | stale backend tests lack applicants | yes for backend tests; automation should use public API |
| TC-A-013 | submitted WAITING_RECEIPT case with APPLY_FEE_LIMIT task | batch filing submit after TC-A-011 blocker cleared | task field semantics incomplete | yes for backend field tests |
| TC-A-015 | domestic invention case with claim_count=12 and fee reduction | case create/update API plus fee generation endpoint, once defined | APPLY_FEE generation contract missing | yes for backend generation test |
| TC-A-017 | APPLY_FEE draft with GOV item | TC-A-015 output or focused backend fixture | upstream draft gap | yes |
| TC-A-019 | one or two APPLY_FEE drafts under same client | TC-A-015 output or focused backend fixture | upstream draft gap | yes |
| TC-A-021 | unsettled bill | TC-A-019 output or focused backend fixture | upstream bill readiness | yes |
| TC-A-023 | bill with SERVICE item and agent/commission rule | TC-A-019 output plus commission arrange | commission seed/config gap | yes |

Mandatory setup rule for all future tasks: case creation must include valid applicants unless the task is intentionally testing applicant errors. Date/status/app-number payloads must remain legal so unrelated rules do not mask the target behavior.

## 7. Allowlist Matrix

| Proposed task | Task file path | Exact closure slice | Allowed files | Shared file conflicts | Serialization group |
| --- | --- | --- | --- | --- | --- |
| BE-A-BATCH-FILING-TEST-MAINT-01 | `tasks/backend/test_maintenance/BE-A-BATCH-FILING-TEST-MAINT-01.md` | add valid applicants to stale batch filing backend tests only | task file, `backend/tests/test_case_batch_filing_action.py`, `backend/tests/test_case_batch_filing_query.py`, artifacts | none with service files | backend batch filing tests |
| BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01 | `tasks/backend/business_logic/BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01.md` | verify/fix full APPLY_FEE_LIMIT task fields after batch filing | task file, `backend/app/modules/cases/service.py`, `backend/tests/test_apply_fee_limit_task_fields.py`, artifacts | `cases/service.py` | cases service |
| PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01 | `tasks/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md` | freeze APPLY_FEE draft calculation contract | task file, product doc, artifacts | none | product docs |
| BE-A-APPLY-FEE-DRAFT-RULE-01 | `tasks/backend/business_logic/BE-A-APPLY-FEE-DRAFT-RULE-01.md` | implement stable APPLY_FEE draft generation path | task file, fees API/service/schema, focused test, artifacts | fees module shared files | fees module |
| BE-A-GOV-PAYLIST-PAYMENT-READINESS-01 | `tasks/backend/business_logic/BE-A-GOV-PAYLIST-PAYMENT-READINESS-01.md` | verify/fix pay list/payment happy path for APPLY GOV items | task file, annuity API/service/schema, focused test, artifacts | annuity module | pay-list module |
| BE-A-APPLY-BILL-READINESS-01 | `tasks/backend/business_logic/BE-A-APPLY-BILL-READINESS-01.md` | verify/fix bill from APPLY_FEE draft | task file, billing API/service/schema, focused test, artifacts | billing module | billing wave 1 |
| BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01 | `tasks/backend/business_logic/BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01.md` | verify/fix payment offset and CaseReceipt happy path | task file, billing API/service/schema, focused test, artifacts | billing module | billing wave 2 |
| BE-A-COMMISSION-RULE-SEED-READINESS-01 | `tasks/backend/business_logic/BE-A-COMMISSION-RULE-SEED-READINESS-01.md` | verify/fix commission rule arrange and generated commission semantics | task file, commission API/service/schema, focused test, artifacts | commission module | commission module |

## 8. Blocker Drain Manifest

Execution order:

1. BE-A-BATCH-FILING-TEST-MAINT-01
2. BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01
3. PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01
4. BE-A-APPLY-FEE-DRAFT-RULE-01
5. BE-A-GOV-PAYLIST-PAYMENT-READINESS-01
6. BE-A-APPLY-BILL-READINESS-01
7. BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01
8. BE-A-COMMISSION-RULE-SEED-READINESS-01

The executable manifest with exact allowed files and verification commands is `tasks/batches/BATCH-A-HAPPY-MAIN-CHAIN-P0-01-BLOCKER-DRAIN.md`.

## 9. Automation Landing Readiness

| Automation task | Testcase | Can start now | Must wait for | Real smoke prerequisites | Stale expectation allowlist risk |
| --- | --- | --- | --- | --- | --- |
| A-AUTO-PY-A-BATCH-SUBMIT-P0-01 | TC-A-011 | no | BE-A-BATCH-FILING-TEST-MAINT-01 and BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02 revalidation | backend running, valid credentials in local shell, fresh run id, explicit empty DB DSN | scan existing A handler tests before edit |
| A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01 | TC-A-013 | no | TC-A-011 backend readiness and BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01 | same | scan for `handle_tc_a_013` assertions |
| A-AUTO-PY-A-APPLY-FEE-DRAFT-P0-01 | TC-A-015 | no | PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01 and BE-A-APPLY-FEE-DRAFT-RULE-01 | same | scan for `handle_tc_a_015` assertions |
| A-AUTO-PY-A-GOV-PAYLIST-P0-01 | TC-A-017 | no | BE-A-GOV-PAYLIST-PAYMENT-READINESS-01 | same | scan for `handle_tc_a_017` assertions |
| A-AUTO-PY-A-APPLY-BILL-P0-01 | TC-A-019 | no | BE-A-APPLY-BILL-READINESS-01 | same | scan for `handle_tc_a_019` assertions |
| A-AUTO-PY-A-PAYMENT-OFFSET-P0-01 | TC-A-021 | no | BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01 | same | scan for `handle_tc_a_021` assertions |
| A-AUTO-PY-A-COMMISSION-P0-01 | TC-A-023 | no | BE-A-COMMISSION-RULE-SEED-READINESS-01 | same | scan for `handle_tc_a_023` assertions |

## 10. Readiness Decision

Readiness Gate result: PASS for blocker discovery and manifest preparation, assuming evidence gate passes.

Batch 2 testcase result: not closed. No testcase should be marked PASS from this readiness task.
