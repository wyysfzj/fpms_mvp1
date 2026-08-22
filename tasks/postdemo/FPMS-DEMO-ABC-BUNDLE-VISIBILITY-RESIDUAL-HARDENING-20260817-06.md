# FPMS-DEMO-ABC-BUNDLE-VISIBILITY-RESIDUAL-HARDENING-20260817-06

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "document", "evidence", "runtime-input", "source"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-BUNDLE-VISIBILITY-RESIDUAL-HARDENING-20260817-06.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Independent findings: third High review `P1-1`, `P1-2`, `P1-3`.
- Dependency: commit `41864d0`; bundle and runner owner is serialized here.

## Exact Closure Slice

Apply default paragraph and character style visibility to unstyled DOCX marker runs. Accept a PDF
marker fragment only with positive finite font size and a finite, non-degenerate effective text
transform. Reject external bundle paths below every `fpms-demo-abc-*` run root, including a name that
matches the requested run ID.

## Explicit Non-Closure

No general document accessibility judgment, OCR, customer bundle approval, remote storage,
production, security, PostgreSQL, or release.

## Allowed Files

- `backend/app/core/demo_bundle.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- `backend/tests/test_demo_abc_local_runner.py`
- this task card

## Verification Commands

Executable RED/GREEN probes for default hidden paragraph/character styles, zero-size PDF text, and
same-ID run-root validator/runner parity; focused pytest, scoped Ruff and diff checks.

## Rollback

Revert the atomic commit.

## Done definition

The three independently reproduced visibility/path bypasses fail closed before any business state.
