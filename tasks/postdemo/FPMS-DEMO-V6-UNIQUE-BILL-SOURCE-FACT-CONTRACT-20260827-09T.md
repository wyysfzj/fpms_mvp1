# FPMS-DEMO-V6-UNIQUE-BILL-SOURCE-FACT-CONTRACT-20260827-09T

Status: ACTIVE
Risk-Tier: MEDIUM
Closure-Tags: ["demo", "test", "fee"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UNIQUE-BILL-SOURCE-FACT-CONTRACT-20260827-09T.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Synchronize the unique accounts-receivable bill test helper with the already accepted Task08AE
service-obligation request contract, where quantity and item identity come from runtime source facts
and the legacy caller-supplied `item_code` is forbidden.

## Explicit Non-Closure

No API, schema, service, runtime source fact, amount, billing behavior, UI, deployment, or release
change.

## Allowed Files

- `backend/tests/test_demo_abc_unique_ar_bill.py`
- `tasks/postdemo/FPMS-DEMO-V6-UNIQUE-BILL-SOURCE-FACT-CONTRACT-20260827-09T.md`

## Done Definition

The three unique-bill tests use the integrated runtime source-fact bundle, no longer send the
forbidden legacy field, and the complete documented fresh-clone backend test set passes.
