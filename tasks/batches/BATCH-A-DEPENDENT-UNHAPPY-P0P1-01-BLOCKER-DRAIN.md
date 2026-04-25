# BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-BLOCKER-DRAIN

## Batch

- Batch ID: BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-BLOCKER-DRAIN
- Source readiness gate: BATCH-A-DEPENDENT-UNHAPPY-P0P1-01-READINESS-GATE
- chosen_runbook: P0-prereq-heavy-story

## Execution Rule

This is a blocker drain manifest, not a single implementation task. Each blocker below must be executed as its own atomic task with independent evidence. Shared files must be serialized. SQLite write tests must not run concurrently.

## Wave 1: Product Contracts

### PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01

- Task file path: tasks/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
- Type: product contract
- Exact closure slice:
  - freeze TC-A-016 invalid fee draft/item contract for a rate-driven API
  - decide whether blank fee code/name and fee type mismatch remain product-required or map to stable backend validation alternatives
- Non-closure:
  - do not modify backend/frontend/pytest code
- Allowed files:
  - tasks/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
  - docs/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
  - artifacts/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01/**
- Verification:
  - test -f tasks/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
  - test -f docs/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
  - rg -n "TC-A-016|FEE_DRAFT|FEE_ITEM|product_decision_required" docs/product/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01.md
- Evidence path: artifacts/PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01/**

### PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01

- Task file path: tasks/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
- Type: product contract
- Exact closure slice:
  - freeze TC-A-018 stale planned-pay-date warning, actual pay info status rule, and paid official-payment edit/audit contract
- Non-closure:
  - do not modify backend/frontend/pytest code
- Allowed files:
  - tasks/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
  - docs/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
  - artifacts/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01/**
- Verification:
  - test -f tasks/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
  - test -f docs/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
  - rg -n "TC-A-018|planned_pay_date|GovPayment|product_decision_required" docs/product/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01.md
- Evidence path: artifacts/PRODUCT-A-GOV-PAYLIST-UNHAPPY-CONTRACT-01/**

## Wave 2: Backend Readiness / Blocker Fixes

### BE-A-APPLY-FEE-ITEM-VALIDATION-01

- Task file path: tasks/backend/business_logic/BE-A-APPLY-FEE-ITEM-VALIDATION-01.md
- Type: backend capability
- Depends on: PRODUCT-A-APPLY-FEE-INVALID-CONTRACT-01 PASS
- Exact closure slice:
  - implement stable TC-A-016-compatible fee draft/item invalid validation that is supported by the frozen contract
- Non-closure:
  - do not implement pay list, bill, payment, commission, or pytest automation
- Allowed files:
  - tasks/backend/business_logic/BE-A-APPLY-FEE-ITEM-VALIDATION-01.md
  - backend/app/modules/fees/service.py
  - backend/app/modules/fees/api.py
  - backend/app/modules/fees/schemas.py
  - backend/tests/test_apply_fee_item_validation.py
  - artifacts/BE-A-APPLY-FEE-ITEM-VALIDATION-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_item_validation.py
  - cd backend && python3 -m ruff format app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_item_validation.py
  - cd backend && python3 -m ruff check app/modules/fees/service.py app/modules/fees/api.py app/modules/fees/schemas.py tests/test_apply_fee_item_validation.py
  - cd backend && pytest tests/test_apply_fee_item_validation.py -q
- Evidence path: artifacts/BE-A-APPLY-FEE-ITEM-VALIDATION-01/**

### BE-A-PAYMENT-OFFSET-UNHAPPY-01

- Task file path: tasks/backend/business_logic/BE-A-PAYMENT-OFFSET-UNHAPPY-01.md
- Type: backend capability
- Exact closure slice:
  - add/verify duplicate client/pay number and future pay-date payment validation for TC-A-022
  - preserve existing offset validation and prepayment behavior
- Non-closure:
  - do not implement commission, frontend, or pytest automation
- Allowed files:
  - tasks/backend/business_logic/BE-A-PAYMENT-OFFSET-UNHAPPY-01.md
  - backend/app/modules/billing/service.py
  - backend/app/modules/billing/api.py
  - backend/app/modules/billing/schemas.py
  - backend/tests/test_payment_offset_unhappy.py
  - artifacts/BE-A-PAYMENT-OFFSET-UNHAPPY-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_unhappy.py
  - cd backend && python3 -m ruff format app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_unhappy.py
  - cd backend && python3 -m ruff check app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_payment_offset_unhappy.py
  - cd backend && pytest tests/test_payment_offset_unhappy.py -q
  - cd backend && pytest tests/test_payment_offset_case_receipt_readiness.py -q
- Evidence path: artifacts/BE-A-PAYMENT-OFFSET-UNHAPPY-01/**

### BE-A-APPLY-BILL-UNHAPPY-01

- Task file path: tasks/backend/business_logic/BE-A-APPLY-BILL-UNHAPPY-01.md
- Type: backend readiness test
- Exact closure slice:
  - verify TC-A-020 bill invalid combinations with focused backend tests
- Non-closure:
  - do not implement payment offset or commission
- Allowed files:
  - tasks/backend/business_logic/BE-A-APPLY-BILL-UNHAPPY-01.md
  - backend/app/modules/billing/service.py
  - backend/app/modules/billing/api.py
  - backend/app/modules/billing/schemas.py
  - backend/tests/test_apply_bill_unhappy.py
  - artifacts/BE-A-APPLY-BILL-UNHAPPY-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_unhappy.py
  - cd backend && python3 -m ruff format app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_unhappy.py
  - cd backend && python3 -m ruff check app/modules/billing/service.py app/modules/billing/api.py app/modules/billing/schemas.py tests/test_apply_bill_unhappy.py
  - cd backend && pytest tests/test_apply_bill_unhappy.py -q
- Evidence path: artifacts/BE-A-APPLY-BILL-UNHAPPY-01/**

### BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01

- Task file path: tasks/backend/business_logic/BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01.md
- Type: backend readiness test
- Exact closure slice:
  - verify wait-pay partial/full receipt settleability and force-settle override for TC-A-024
- Non-closure:
  - do not implement settlement execution or pytest automation
- Allowed files:
  - tasks/backend/business_logic/BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01.md
  - backend/app/modules/commission/service.py
  - backend/app/modules/commission/api.py
  - backend/app/modules/commission/schemas.py
  - backend/tests/test_commission_waitpay_threshold.py
  - artifacts/BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01/**
- Verification:
  - cd backend && python3 -m ruff check --fix app/modules/commission/service.py app/modules/commission/api.py app/modules/commission/schemas.py tests/test_commission_waitpay_threshold.py
  - cd backend && python3 -m ruff format app/modules/commission/service.py app/modules/commission/api.py app/modules/commission/schemas.py tests/test_commission_waitpay_threshold.py
  - cd backend && python3 -m ruff check app/modules/commission/service.py app/modules/commission/api.py app/modules/commission/schemas.py tests/test_commission_waitpay_threshold.py
  - cd backend && pytest tests/test_commission_waitpay_threshold.py -q
- Evidence path: artifacts/BE-A-COMMISSION-WAITPAY-THRESHOLD-READINESS-01/**

## Drain Decision

- TC-A-012 can proceed directly to automation.
- TC-A-016 must wait for product and backend fee invalid blockers.
- TC-A-018 must wait for product contract before backend/frontend implementation.
- TC-A-020 can proceed after backend unhappy evidence.
- TC-A-022 must wait for BE-A-PAYMENT-OFFSET-UNHAPPY-01.
- TC-A-024 can proceed after backend readiness evidence.
