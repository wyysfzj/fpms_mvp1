# FPMS-DEMO-INTEGRATED-A-BROWSER-LOGIN-20260821-01B

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "browser", "liveness"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BROWSER-LOGIN-20260821-01B.md
Role: Implementer
Dependencies: ["FPMS-DEMO-INTEGRATED-A-BROWSER-CONTRACT-20260821-01 APPROVED 0/0/0"]

## Exact Closure Slice

Replace only the two stale placeholder-based login locators in the canonical Integrated A browser
spec with locators bound to the current visible Simplified-Chinese form labels. Preserve the
approved static API boundary and advance the controller from login to the existing IA-00 RED.

## Explicit Non-Closure

No login product change, authentication change, browser-contract redesign, bundle or business
implementation, later IA checkpoint, security, production, broad/product/release gate or readiness
claim.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- `backend/tests/test_demo_integrated_a_runner.py`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BROWSER-LOGIN-20260821-01B.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-BROWSER-LOGIN-20260821-01B/**`

## Verification Commands

- RED/GREEN the exact login locator contract in `backend/tests/test_demo_integrated_a_runner.py`.
- Run the canonical static contract, Playwright list, scoped Ruff and one controller invocation.
- Bind an exact clean candidate to independent High review.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-BROWSER-LOGIN-20260821-01B/**`

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

The real current login page is operable through visible label-bound fields, the static API boundary
remains green, and one clean-candidate controller run reaches the pre-existing IA-00 RED without
waiting for a global test timeout. Independent High review is 0/0/0.
