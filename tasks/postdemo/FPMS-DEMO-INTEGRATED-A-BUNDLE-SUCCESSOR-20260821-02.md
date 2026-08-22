# FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "runtime-input", "source-authority", "lineage"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02.md
Role: Implementer
Source-Decision-Refs: ["DEC-INTEGRATED-DEMO-A-20260821", "DEC-INTEGRATED-DEMO-A-API-BOUNDARY-20260821"]
Dependencies: ["FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01 APPROVED 0/0/0"]

## Exact Closure Slice

Add an explicit `fpms.demo-input-bundle/integrated-a-v1` parser and immutable snapshot beside the
unchanged ABC v1 contract. Freeze one template, one SERVICE rate, the ordered 12 fictional
evidence roles, exact OA1/OA2 and grant-original/replacement metadata, pairwise distinct critical
hashes, and an authority record containing exactly 13 file digests. Add the synthetic builder used
by the integrated controller and advance the behavioral RED beyond missing builder to IA-00.

## Explicit Non-Closure

No product/business writes, UI provenance implementation, evidence review reconciliation,
lifecycle transition changes, finance changes, customer activation, official-fee truth,
production, PostgreSQL, security, broad/product/release gate or readiness claim.

## Allowed Files

- `backend/app/core/demo_bundle.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_integrated_a_runner.py`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02/**`

## Verification Commands

- RED then GREEN: integrated cases in `backend/tests/test_demo_abc_runtime_bundle.py`.
- GREEN: legacy v1 plus integrated bundle and focused runner tests.
- Ruff on the four Python files.
- One headless controller invocation that passes bundle construction/preflight and reaches the
  first IA-00 product/UI RED.
- Exact task allowlist and independent High review of the committed candidate.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-PROVENANCE-UI-20260821-03`
- `FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04`
- `FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05`
- `FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06`
- `FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07`
- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

Old `fpms.demo-input-bundle/v1` remains byte-contract compatible; integrated bundles accept only
the exact schema/contract/purpose/role order and immutable descriptors. Missing, extra, aliased,
duplicated, semantically reused, hash-conflicting or authority-digest-conflicting input fails before
business services open. The runner builds only synthetic input outside repo/storage and no later
ordinal or product write is implemented. Exact candidate independent review is `0/0/0`.
