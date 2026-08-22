# FPMS-DEMO-ABC-BUNDLE-HARDENING-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "runtime-input", "source-authority", "template", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-BUNDLE-HARDENING-20260817-01.md

## Exact Closure Slice

Correct bundle-v1 validation for role-specific OA metadata, exact DOCX placeholder identity and
structurally parsed first-page-visible PDF markers. Reject a symlink bundle root, materialize one
content-addressed read-only copy inside the fresh run before database migration, and serve one
process-cached snapshot rather than rereading mutable external input.

## Explicit Non-Closure

No customer-authorized bundle is invented. Exact customer authority remains an external input gate
and the result cannot be named `DEMO_READY` until that record and actual bundle arrive. No generic
template administration, production storage, security, OA execution, billing or release work.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-COMMAND-RECONCILIATION-20260817-01`
- `FPMS-DEMO-ABC-EVIDENCE-REBUILD-20260817-01`

## Allowed Files

- `backend/pyproject.toml`
- `backend/fpms_api.egg-info/requires.txt`
- `backend/app/core/demo_bundle.py`
- `backend/app/modules/fees/demo_service.py`
- `backend/scripts/run_local_demo_abc.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- `backend/tests/test_demo_abc_local_runner.py`
- `backend/tests/test_demo_abc_runtime_service_draft.py`
- `artifacts/FPMS-DEMO-ABC-BUNDLE-HARDENING-20260817-01/**`

## Verification Commands

1. RED proves invalid role metadata, placeholder drift, pseudo-PDF, root symlink and mutable external
   bytes are not closed by the current implementation.
2. GREEN passes the focused bundle/runner/service tests and scoped Ruff.
3. A fresh bootstrap proves the validated copy precedes database migration and is read-only.
4. Exact allowlist/diff checks pass; no broad or release gate runs.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-BUNDLE-HARDENING-20260817-01/`

## Rollback

Revert the atomic product commit. Delete only the exact temporary test run roots after evidence.

## Done definition

Technical bundle validation and immutable runtime use pass targeted checks. Customer authority and
independent High acceptance remain explicit gates.
