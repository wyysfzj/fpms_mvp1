# FPMS-DEMO-ABC-BUNDLE-VISIBILITY-VALIDATOR-HARDENING-20260817-04

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "document", "evidence", "runtime-input", "source"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-BUNDLE-VISIBILITY-VALIDATOR-HARDENING-20260817-04.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Controlling design: `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`.
- Independent findings: second High review `P1-3`, `P1-4`.
- Dependency: commit `6bde8bb`; runtime bundle and local runner owner is serialized here.

## Exact Closure Slice

Reject DOCX fictional-demo markers hidden by direct or inherited paragraph/character styles. Accept a
PDF marker only from a first-page, on-page text fragment using a visible non-clipping render mode.
Make the standalone validator and local runner share the same rejection of configured product storage
and prior `fpms-demo-abc-*` run roots.

## Explicit Non-Closure

No generic document renderer, OCR, customer input creation/approval, remote storage, production,
security, PostgreSQL, or release.

## Allowed Files

- `backend/app/core/demo_bundle.py`
- `backend/scripts/run_local_demo_abc.py`
- `backend/scripts/validate_demo_bundle.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- `backend/tests/test_demo_abc_local_runner.py`
- this task card

## Verification Commands

1. RED tests accept an inherited-style hidden DOCX marker, invisible PDF text, or validator-only
   forbidden-root input.
2. GREEN rejects each with `DEMO_INPUT_INVALID` before business state or run-directory creation.
3. Focused pytest, scoped Ruff and diff checks pass.

## Rollback

Revert the atomic commit.

## Done definition

The activation preflight cannot certify a bundle whose warning is non-visible or whose input path is
inside protected product/run storage, and validator/runner decisions are identical. Independent High
acceptance remains required.
