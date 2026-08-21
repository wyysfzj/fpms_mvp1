# FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "lifecycle", "lineage", "fee", "payment", "browser-contract"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01.md
Role: Implementer

## Exact Closure Slice

Create the canonical IA-00…IA-18 browser contract, its static fail-closed checker, and a minimal
integrated controller that explicitly selects that spec and supports one isolated run. Preserve the
first executable behavioral RED caused by the absent integrated-a-v1 bundle builder.

## Explicit Non-Closure

No integrated bundle implementation, lifecycle/product fix, finance change, customer activation,
official-fee truth, production, PostgreSQL, security, broad/product/release gate or readiness claim.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_integrated_a_runner.py`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01/**`

## Verification Commands

- RED then GREEN: static Node contract.
- RED then GREEN: focused runner pytest.
- Ruff on the new Python files.
- One headless controller invocation that reaches the exact missing-integrated-bundle RED.
- Exact task allowlist and independent High review of the committed candidate.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01/**`

## Remaining Follow-Up Task IDs

- None within this atomic closure. Approved plan ordinals 02–10 remain separately owned.

## Done Definition

The static contract proves the forbidden constructs and required IA/role/lineage tokens; the runner
CLI accepts `--artifact`, `--runs 1|2`, and `--headless`, selects only the integrated spec, keeps
business writes in the browser/public surfaces, cleans exact temporary roots, and the recorded
behavioral RED is the missing integrated-a-v1 builder rather than an earlier runner defect. Exact
candidate independent review is `0/0/0`; no later ordinal is implemented.
