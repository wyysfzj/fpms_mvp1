# BATCH-A-HAPPY-MAIN-CHAIN-P0-01-BLOCKER-DRAIN

## Batch

- Batch ID: BATCH-A-HAPPY-MAIN-CHAIN-P0-01-BLOCKER-DRAIN
- Source readiness gate: BATCH-A-HAPPY-MAIN-CHAIN-P0-01-READINESS-GATE
- chosen_runbook: P0-prereq-heavy-story

## Execution Rule

This is a blocker drain manifest, not a single implementation task. Each blocker below must be executed as its own atomic task with independent evidence. Shared files must be serialized. SQLite write tests must not run concurrently.

## Wave 1: Clear Known Stale Backend Test Blocker

### BE-A-BATCH-FILING-TEST-MAINT-01

- Task file path: tasks/backend/test_maintenance/BE-A-BATCH-FILING-TEST-MAINT-01.md
- Type: test maintenance
- Depends on: BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02 implementation state
- Exact closure slice:
  - update stale backend batch filing tests so their case creation setup includes valid applicants
  - preserve existing batch filing business assertions
  - revalidate BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02 targeted regressions
- Non-closure:
  - do not modify batch filing service/API/schema
  - do not change status transition, submitted date, exam request, candidate query, document, or task side-effect assertions
- Allowed files:
  - tasks/backend/test_maintenance/BE-A-BATCH-FILING-TEST-MAINT-01.md
  - backend/tests/test_case_batch_filing_action.py
  - backend/tests/test_case_batch_filing_query.py
  - artifacts/BE-A-BATCH-FILING-TEST-MAINT-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix tests/test_case_batch_filing_action.py tests/test_case_batch_filing_query.py
  - cd backend && python3 -m ruff format tests/test_case_batch_filing_action.py tests/test_case_batch_filing_query.py
  - cd backend && python3 -m ruff check tests/test_case_batch_filing_action.py tests/test_case_batch_filing_query.py
  - cd backend && pytest tests/test_case_batch_filing_action.py -q
  - cd backend && pytest tests/test_case_batch_filing_query.py -q
  - cd backend && pytest tests/test_case_batch_filing_side_effects.py -q
  - ./scripts/task_validate.sh BE-A-BATCH-FILING-TEST-MAINT-01
- Evidence path: artifacts/BE-A-BATCH-FILING-TEST-MAINT-01/**
- Serialization group: backend batch filing tests
- Drain status: ready for atomic execution

## Wave 2: TC-A-013 Deadline Task Readiness

### BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01

- Task file path: tasks/backend/business_logic/BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01.md
- Type: backend capability
- Depends on: BE-A-BATCH-FILING-TEST-MAINT-01 PASS and BE-A-BATCH-SUBMIT-SIDE-EFFECTS-02 revalidated
- Exact closure slice:
  - ensure batch filing generated `APPLY_FEE_LIMIT` tasks include stable base date, deadline, internal deadline, reminder fields, worker/supervisor assignment where configured, status OPEN, and TaskLog creation semantics
  - preserve existing batch filing side effects and response contract
- Non-closure:
  - do not implement pytest handler TC-A-013
  - do not implement fee draft, pay list, bill, payment, or commission behavior
- Allowed files:
  - tasks/backend/business_logic/BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01.md
  - backend/app/modules/cases/service.py
  - backend/tests/test_apply_fee_limit_task_fields.py
  - artifacts/BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix app/modules/cases/service.py tests/test_apply_fee_limit_task_fields.py
  - cd backend && python3 -m ruff format app/modules/cases/service.py tests/test_apply_fee_limit_task_fields.py
  - cd backend && python3 -m ruff check app/modules/cases/service.py tests/test_apply_fee_limit_task_fields.py
  - cd backend && pytest tests/test_apply_fee_limit_task_fields.py -q
  - cd backend && pytest tests/test_case_batch_filing_side_effects.py -q
  - ./scripts/task_validate.sh BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01
- Evidence path: artifacts/BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01/**
- Serialization group: backend/app/modules/cases/service.py
- Drain status: task authoring ready; product defaults for assignment/reminders must be recorded in task summary if existing template values are absent

## Wave 3: TC-A-015 Apply Fee Draft Contract And Backend

### PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01

- Task file path: tasks/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
- Type: product contract
- Depends on: none
- Exact closure slice:
  - freeze product contract for generating APPLY_FEE drafts for domestic invention cases, claim-count excess fee, fee reduction, service fee, discount, totals, and required fee-rate seed values
- Non-closure:
  - do not modify backend/frontend/pytest code
- Allowed files:
  - tasks/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
  - docs/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
  - artifacts/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01/**
- Verification:
  - test -f tasks/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
  - test -f docs/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
  - rg -n "APPLY_FEE|claim|fee reduction|service fee|FeeRate" docs/product/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01.md
  - ./scripts/task_validate.sh PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01
- Evidence path: artifacts/PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01/**
- Serialization group: product docs only
- Drain status: required before backend implementation because current endpoints are generic fee CRUD, not a stable APPLY_FEE generation contract

### BE-A-APPLY-FEE-DRAFT-RULE-01

- Task file path: tasks/backend/business_logic/BE-A-APPLY-FEE-DRAFT-RULE-01.md
- Type: backend capability
- Depends on: PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01 PASS
- Exact closure slice:
  - implement or expose the minimal backend rule/API path needed to generate one APPLY_FEE draft and fee items for TC-A-015 using existing FeeDraft, FeeItem, and FeeRate models
- Non-closure:
  - do not implement pay list, bill, payment, or commission behavior
  - do not implement pytest automation handler
- Allowed files:
  - tasks/backend/business_logic/BE-A-APPLY-FEE-DRAFT-RULE-01.md
  - backend/app/modules/fees/service.py
  - backend/app/modules/fees/api.py
  - backend/app/modules/fees/schemas.py
  - backend/tests/test_apply_fee_draft_rule.py
  - artifacts/BE-A-APPLY-FEE-DRAFT-RULE-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_draft_rule.py
  - cd backend && python3 -m ruff format app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_draft_rule.py
  - cd backend && python3 -m ruff check app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_draft_rule.py
  - cd backend && pytest tests/test_apply_fee_draft_rule.py -q
  - ./scripts/task_validate.sh BE-A-APPLY-FEE-DRAFT-RULE-01
- Evidence path: artifacts/BE-A-APPLY-FEE-DRAFT-RULE-01/**
- Serialization group: fees module API/service/schema
- Drain status: waits for product contract

## Wave 4: Downstream Backend Readiness Tests

### BE-A-GOV-PAYLIST-PAYMENT-READINESS-01

- Task file path: tasks/backend/business_logic/BE-A-GOV-PAYLIST-PAYMENT-READINESS-01.md
- Type: backend readiness test / capability fix if needed
- Depends on: BE-A-APPLY-FEE-DRAFT-RULE-01 PASS
- Exact closure slice:
  - verify or minimally fix the existing pay-list and official-payment flow for APPLY GOV fee items: create pay list, export/list support, register payment, status PAID, paid amount visibility
- Non-closure:
  - do not implement bill/payment offset/commission
- Allowed files:
  - tasks/backend/business_logic/BE-A-GOV-PAYLIST-PAYMENT-READINESS-01.md
  - backend/app/modules/annuity/service.py
  - backend/app/modules/annuity/api.py
  - backend/app/modules/annuity/schemas.py
  - backend/tests/test_apply_gov_paylist_readiness.py
  - artifacts/BE-A-GOV-PAYLIST-PAYMENT-READINESS-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix app/modules/annuity/service.py app/modules/annuity/api.py app/modules/annuity/schemas.py tests/test_apply_gov_paylist_readiness.py
  - cd backend && python3 -m ruff format app/modules/annuity/service.py app/modules/annuity/api.py app/modules/annuity/schemas.py tests/test_apply_gov_paylist_readiness.py
  - cd backend && python3 -m ruff check app/modules/annuity/service.py app/modules/annuity/api.py app/modules/annuity/schemas.py tests/test_apply_gov_paylist_readiness.py
  - cd backend && pytest tests/test_apply_gov_paylist_readiness.py -q
  - ./scripts/task_validate.sh BE-A-GOV-PAYLIST-PAYMENT-READINESS-01
- Evidence path: artifacts/BE-A-GOV-PAYLIST-PAYMENT-READINESS-01/**
- Serialization group: annuity/pay-list module
- Drain status: waits for APPLY_FEE draft backend

### BE-A-APPLY-BILL-READINESS-01

- Task file path: tasks/backend/business_logic/BE-A-APPLY-BILL-READINESS-01.md
- Type: backend readiness test / capability fix if needed
- Depends on: BE-A-APPLY-FEE-DRAFT-RULE-01 PASS
- Exact closure slice:
  - verify or minimally fix bill generation from APPLY_FEE drafts, BillItem binding, totals, balance, and UNSETTLED status
- Non-closure:
  - do not implement customer payment offset or commission settlement
- Allowed files:
  - tasks/backend/business_logic/BE-A-APPLY-BILL-READINESS-01.md
  - backend/app/modules/billing/service.py
  - backend/app/modules/billing/api.py
  - backend/app/modules/billing/schemas.py
  - backend/tests/test_apply_bill_readiness.py
  - artifacts/BE-A-APPLY-BILL-READINESS-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_readiness.py
  - cd backend && python3 -m ruff format app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_readiness.py
  - cd backend && python3 -m ruff check app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_readiness.py
  - cd backend && pytest tests/test_apply_bill_readiness.py -q
  - ./scripts/task_validate.sh BE-A-APPLY-BILL-READINESS-01
- Evidence path: artifacts/BE-A-APPLY-BILL-READINESS-01/**
- Serialization group: billing module
- Drain status: waits for APPLY_FEE draft backend

### BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01

- Task file path: tasks/backend/business_logic/BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01.md
- Type: backend readiness test / capability fix if needed
- Depends on: BE-A-APPLY-BILL-READINESS-01 PASS
- Exact closure slice:
  - verify or minimally fix payment, offset, bill balance/status, and CaseReceipt received/arrears behavior for TC-A-021
- Non-closure:
  - do not implement over-offset unhappy paths
  - do not implement commission
- Allowed files:
  - tasks/backend/business_logic/BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01.md
  - backend/app/modules/billing/service.py
  - backend/app/modules/billing/api.py
  - backend/app/modules/billing/schemas.py
  - backend/tests/test_payment_offset_case_receipt_readiness.py
  - artifacts/BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_case_receipt_readiness.py
  - cd backend && python3 -m ruff format app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_case_receipt_readiness.py
  - cd backend && python3 -m ruff check app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_case_receipt_readiness.py
  - cd backend && pytest tests/test_payment_offset_case_receipt_readiness.py -q
  - ./scripts/task_validate.sh BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01
- Evidence path: artifacts/BE-A-PAYMENT-OFFSET-CASE-RECEIPT-READINESS-01/**
- Serialization group: billing module; serialize after BE-A-APPLY-BILL-READINESS-01
- Drain status: waits for bill readiness

### BE-A-COMMISSION-RULE-SEED-READINESS-01

- Task file path: tasks/backend/business_logic/BE-A-COMMISSION-RULE-SEED-READINESS-01.md
- Type: seed/config readiness test / capability fix if needed
- Depends on: BE-A-APPLY-BILL-READINESS-01 PASS
- Exact closure slice:
  - verify or minimally fix commission rule arrange path, service-fee base, main/co-agent split, 70/30 amounts, WaitPay/ForceSettle initial fields, and available-to-settle query path
- Non-closure:
  - do not implement settlement execution
  - do not implement pytest automation handler
- Allowed files:
  - tasks/backend/business_logic/BE-A-COMMISSION-RULE-SEED-READINESS-01.md
  - backend/app/modules/commission/service.py
  - backend/app/modules/commission/api.py
  - backend/app/modules/commission/schemas.py
  - backend/tests/test_commission_rule_seed_readiness.py
  - artifacts/BE-A-COMMISSION-RULE-SEED-READINESS-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix app/modules/commission/service.py app/modules/commission/api.py app/modules/commission/schemas.py tests/test_commission_rule_seed_readiness.py
  - cd backend && python3 -m ruff format app/modules/commission/service.py app/modules/commission/api.py app/modules/commission/schemas.py tests/test_commission_rule_seed_readiness.py
  - cd backend && python3 -m ruff check app/modules/commission/service.py app/modules/commission/api.py app/modules/commission/schemas.py tests/test_commission_rule_seed_readiness.py
  - cd backend && pytest tests/test_commission_rule_seed_readiness.py -q
  - ./scripts/task_validate.sh BE-A-COMMISSION-RULE-SEED-READINESS-01
- Evidence path: artifacts/BE-A-COMMISSION-RULE-SEED-READINESS-01/**
- Serialization group: commission module
- Drain status: waits for bill readiness

## Automation Landing After Drain

Only after the relevant backend/test-maint blockers pass may these automation tasks resume, each as a separate atomic task:

1. A-AUTO-PY-A-BATCH-SUBMIT-P0-01
2. A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01
3. A-AUTO-PY-A-APPLY-FEE-DRAFT-P0-01
4. A-AUTO-PY-A-GOV-PAYLIST-P0-01
5. A-AUTO-PY-A-APPLY-BILL-P0-01
6. A-AUTO-PY-A-PAYMENT-OFFSET-P0-01
7. A-AUTO-PY-A-COMMISSION-P0-01
