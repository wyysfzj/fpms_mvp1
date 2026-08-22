# FPMS-DEMO-ABC-BUNDLE-AUTHORITY-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "runtime-input", "source-authority", "fee"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-BUNDLE-AUTHORITY-20260817-01.md

## Exact Closure Slice

Require an externally pinned, exact authority record before bundle validation or business writes.
The record must be `APPROVED`, bind actor/time/version, exact decision bytes, bundle ID/version,
raw manifest digest, both source digests and every template/evidence file digest. Its own SHA-256 is
provided independently through the local runner environment and recorded in run metadata.

## Explicit Non-Closure

Do not invent the customer's authority record or actual template/rate bytes. Tests may create an
isolated synthetic approved record, but `DEMO_READY` remains blocked until the customer-provided
record and bundle are supplied. No production trust service, signatures, PKI, security or release.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-COMMAND-RECONCILIATION-20260817-01`
- `FPMS-DEMO-ABC-EVIDENCE-REBUILD-20260817-01`

## Allowed Files

- `backend/app/core/demo_bundle.py`
- `backend/app/modules/fees/demo_service.py`
- `backend/scripts/validate_demo_bundle.py`
- `backend/scripts/run_local_demo_abc.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- `backend/tests/test_demo_abc_local_runner.py`
- `backend/tests/test_demo_abc_runtime_service_draft.py`
- `artifacts/FPMS-DEMO-ABC-BUNDLE-AUTHORITY-20260817-01/**`

## Verification Commands

1. RED proves missing, self-declared, drifted or non-approved authority can currently pass.
2. GREEN proves exact record/hash/decision/source/file binding and no-write failure.
3. Runner metadata carries the authority digest and copied bundle remains immutable.
4. Focused pytest, Ruff and exact scope checks pass; no broad or release gate runs.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-BUNDLE-AUTHORITY-20260817-01/`

## Rollback

Revert the atomic product commit. No authority is inferred from test fixtures.

## Done definition

Code rejects any runtime bundle without its independently pinned approved authority record. Actual
customer input and independent High acceptance remain explicit final gates.
