# FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "lifecycle", "lineage", "fee", "payment", "browser-contract"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01.md
Role: Implementer
Source-Decision-Refs: ["DEC-INTEGRATED-DEMO-A-20260821", "DEC-INTEGRATED-DEMO-A-API-BOUNDARY-20260821"]
Dependencies: ["FPMS-DEMO-INTEGRATED-A-API-BOUNDARY-20260821-01A APPROVED 0/0/0"]

## Exact Closure Slice

Create the canonical IA-00…IA-18 browser contract, its static fail-closed checker, and a minimal
integrated controller that explicitly selects that spec and supports one isolated run. Preserve the
first executable behavioral RED caused by the absent integrated-a-v1 bundle builder. Evidence
upload/review remains visible-UI-only; lifecycle operations lacking visible UI use only the exact
method/path allowlist approved by `DEC-INTEGRATED-DEMO-A-API-BOUNDARY-20260821`.

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

- `FPMS-DEMO-INTEGRATED-A-BUNDLE-SUCCESSOR-20260821-02`
- `FPMS-DEMO-INTEGRATED-A-PROVENANCE-UI-20260821-03`
- `FPMS-DEMO-INTEGRATED-A-EVIDENCE-REVIEW-20260821-04`
- `FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05`
- `FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06`
- `FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07`
- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

The static contract proves the forbidden constructs, exact lifecycle public-API allowlist and
required IA/role/lineage tokens; the runner CLI accepts `--artifact`, `--runs 1|2`, and
`--headless`, selects only the integrated spec, keeps attachment/review writes in visible UI and
other allowed lifecycle calls in the single audited helper, cleans exact temporary roots, and the
recorded behavioral RED is the missing integrated-a-v1 builder rather than an earlier runner
defect. Exact candidate independent review is `0/0/0`; no later ordinal is implemented.
