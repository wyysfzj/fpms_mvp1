# FPMS-DEMO-INTEGRATED-A-SERVICE-OBLIGATION-DETAIL-20260822-08A

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "fee", "lifecycle", "data", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-SERVICE-OBLIGATION-DETAIL-20260822-08A.md
Role: Implementer
Dependencies: ["FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07 APPROVED 0/0/0"]

## Exact Closure Slice

Close the concrete owner gap discovered by Task 8 before IA-13: after a verified SERVICE
obligation receives PAY instruction and creates one linked draft/item, the canonical
`get_fee_obligation` reader and lifecycle overlay must accept that stored SERVICE relationship.
They must return the same obligation identity, SERVICE line, CREATED draft status,
NOT_APPLICABLE official-evidence status and NOT_CREATED PayList status. The reader must continue to
reject mixed-domain, malformed, partially populated official-payment and cross-case relations.

## Explicit Non-Closure

No fee/rate amount or source change, no official-fee activation, no obligation/draft creation
contract change, no PayList or government-payment creation, no billing/payment/offset UI, no IA-14
through IA-18 execution, no schema/migration, security, production/PostgreSQL or broad/product/
release gate.

## Allowed Files

- `backend/app/modules/fees/obligation_service.py`
- `backend/tests/test_demo_abc_runtime_service_draft.py`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-SERVICE-OBLIGATION-DETAIL-20260822-08A.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-SERVICE-OBLIGATION-DETAIL-20260822-08A/**`

## Verification Commands

- Retain the Task-8 focused RED showing `FEE_OBLIGATION_STORED_STATE_INVALID` for a legitimate
  SERVICE draft link.
- Add focused negative coverage proving SERVICE relations cannot carry GovPayment/PayList facts or
  cross case/currency/domain identities.
- Run the service-draft focused spec and Ruff on the exact changed Python files.
- Prove exact scope, candidate identity and independent High review.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-SERVICE-OBLIGATION-DETAIL-20260822-08A/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

The exact legitimate SERVICE draft relationship reads through both canonical detail and lifecycle
overlay with authoritative identities/statuses, malformed relation regressions remain fail-closed,
focused checks pass, and the exact candidate receives independent High APPROVED 0/0/0.
