# FPMS-DEMO-ABC-PDF-BUFFERED-TEXT-HARDENING-20260817-08

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "document", "evidence", "runtime-input"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-PDF-BUFFERED-TEXT-HARDENING-20260817-08.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Independent finding: fifth High review residual `P1`.
- Dependency: commit `a158877`.

## Exact Closure Slice

Validate effective visibility at every PDF text-show operator rather than attributing pypdf's buffered
text to the final `BT..ET` state. Fail closed if any first-page text show uses an invisible render
mode, clipping, missing/non-positive font size, zero/non-finite horizontal scaling, degenerate
transform, or off-page origin. Cover both hidden-marker-first and visible-marker-first mixed `Tz`
orders so buffering cannot reverse the result.

## Explicit Non-Closure

No generic PDF normalization, OCR, customer input creation, production, or release.

## Allowed Files

- `backend/app/core/demo_bundle.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- this task card

## Verification Commands

Executable mixed-order RED/GREEN probes, full runtime-bundle focused pytest, scoped Ruff and diff.

## Rollback

Revert the atomic commit.

## Done definition

Buffered text extraction cannot assign an invisible marker the visibility state of a later fragment.
