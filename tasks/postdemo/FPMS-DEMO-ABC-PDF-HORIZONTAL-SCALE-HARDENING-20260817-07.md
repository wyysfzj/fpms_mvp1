# FPMS-DEMO-ABC-PDF-HORIZONTAL-SCALE-HARDENING-20260817-07

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "document", "evidence", "runtime-input"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-PDF-HORIZONTAL-SCALE-HARDENING-20260817-07.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Independent finding: fourth High review residual `P1`.
- Dependency: commit `de00135`.

## Exact Closure Slice

Track PDF text horizontal scaling (`Tz`, default 100) with graphics-state save/restore and reject a
marker fragment when scaling is non-finite or effectively zero.

## Explicit Non-Closure

No general PDF renderer/OCR, customer input creation, production, or release.

## Allowed Files

- `backend/app/core/demo_bundle.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- this task card

## Verification Commands

Executable zero-`Tz` RED/GREEN probe, complete runtime-bundle focused pytest, scoped Ruff and diff.

## Rollback

Revert the atomic commit.

## Done definition

A marker horizontally collapsed to zero cannot satisfy the visible fictional-warning gate.
