# FPMS-DEMO-ABC-PDF-COMPOSITE-TEXT-FAIL-CLOSED-20260817-09

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "document", "evidence", "runtime-input"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-PDF-COMPOSITE-TEXT-FAIL-CLOSED-20260817-09.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Independent finding: sixth High review residual `P1`.
- Dependency: commit `6220dca`.

## Exact Closure Slice

Fail closed on PDF composite text-show operators `TJ`, `'`, and `"`, whose per-fragment painted
origins cannot be established from pypdf's pre-operand matrix. The demo bundle accepts only `Tj`
text shows that pass the existing per-show state/transform/on-page checks.

## Explicit Non-Closure

No PDF layout engine, generic PDF normalization, OCR, customer input creation, production, or release.

## Allowed Files

- `backend/app/core/demo_bundle.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- this task card

## Verification Commands

Executable off-page quote/double-quote/TJ RED/GREEN probes, full runtime-bundle pytest, scoped Ruff.

## Rollback

Revert the atomic commit.

## Done definition

No composite text operator can borrow a safe pre-operand origin to satisfy the visible marker gate.
