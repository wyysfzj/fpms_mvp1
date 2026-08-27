# FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPT-CLEANUP-20260827-08AR

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["demo", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPT-CLEANUP-20260827-08AR.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

If exact finalized-run cleanup fails after actor receipt materialization, remove the unpublished
PASS receipt before recording FAILED so no failed terminal path leaves a PASS artifact.

## Explicit Non-Closure

No receipt schema, observer, business flow, cleanup target, retry, generic transaction, Task 09
docs, or release change.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPT-CLEANUP-20260827-08AR.md`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_v6_ui_session.py`

## Done Definition

A simulated cleanup failure preserves the run, records FAILED, and leaves no `pass-receipt.json`;
successful finalization behavior remains unchanged.
