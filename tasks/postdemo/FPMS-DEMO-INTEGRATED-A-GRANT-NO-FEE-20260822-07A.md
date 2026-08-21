# FPMS-DEMO-INTEGRATED-A-GRANT-NO-FEE-20260822-07A

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "grant", "lifecycle", "fee", "blocker"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-GRANT-NO-FEE-20260822-07A.md
Role: Implementer
Dependencies: ["FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07 live IA-10 RED LIFECYCLE_RULE_DECISION_INVALID"]

## Exact Closure Slice

Close only the proven IA-10 lifecycle-rule blocker. In `FPMS_ENV=demo` with exact
`FPMS_DEMO_SCOPE=LOCAL_ABC_E2E`, accept a canonical SHA-256-bound grant-fee snapshot whose `lines`
array is empty, so reviewed grant evidence can advance lifecycle while official-fee authority
remains unconfigured. Preserve every other grant event, evidence, projection and lineage check.
Outside that exact local-demo profile, the same empty snapshot must remain invalid.

## Explicit Non-Closure

No grant service/API/UI change, no fee item/obligation/draft/payable creation, no official amount
inference, no nonempty snapshot relaxation, no Task-7 browser implementation change and no broad,
product, production or release gate.

## Allowed Files

- `backend/app/modules/cases/lifecycle_rules.py`
- `backend/tests/test_demo_integrated_grant_rule.py`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-GRANT-NO-FEE-20260822-07A.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-GRANT-NO-FEE-20260822-07A/**`

## Verification Commands

- Run the new exact demo/non-demo rule test RED/GREEN.
- Run the focused existing grant-registration lifecycle rule suite and Ruff.
- Prove exact scope, candidate identity and independent High review.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-GRANT-NO-FEE-20260822-07A/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07`
- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

Exact local-demo empty snapshot returns the required grant projection, the identical non-demo
command returns no decision, all focused checks pass, and the exact candidate receives independent
High `APPROVED` with `P0/P1/P2 = 0/0/0`.
