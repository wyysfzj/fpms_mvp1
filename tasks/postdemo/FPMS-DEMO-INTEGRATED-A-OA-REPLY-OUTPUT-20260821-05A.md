# FPMS-DEMO-INTEGRATED-A-OA-REPLY-OUTPUT-20260821-05A

Status: ACTIVE
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["demo", "oa", "documents", "ui", "evidence"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-OA-REPLY-OUTPUT-20260821-05A.md
Role: Implementer
Dependencies: ["FPMS-DEMO-INTEGRATED-A-FIRST-OA-20260821-05 APPROVED 0/0/0"]

## Exact Closure Slice

Close the concrete owner gap discovered before IA-07: the local rehearsal controller materializes
exactly six per-run OA reply output files (Word statement, PDF fidelity copy and modified claims for
OA1 and OA2) outside the immutable runtime-input bundle, labels them
`SYNTHETIC_TEST_OUTPUT`, records path/role/sequence/media type/SHA-256, and passes only that
redacted descriptor JSON to the browser. These files are internal fictional work output, not
official/customer input and not lifecycle evidence authority.

Make the existing OA reply page expose visible Simplified-Chinese completion controls for the
backend's exact six required checklist codes. Remove the four mismatched action codes from this
page. No checklist is auto-completed and no archive/evidence gate is weakened.

## Explicit Non-Closure

No IA-07…18 execution, no receipt/archive write, no bundle schema or 12-role change, no lifecycle
API allowlist change, no evidence upload/review shortcut, no seed/enrichment business object, no
official/customer/legal truth, security, production/PostgreSQL, broad/product/release gate.

## Allowed Files

- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_integrated_oa_reply_output.py`
- `frontend/src/modules/documents/pages/OAReplyPackage.vue`
- `frontend/tests/oa-reply-checklist-actions.mjs`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-OA-REPLY-OUTPUT-20260821-05A.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-OA-REPLY-OUTPUT-20260821-05A/**`

## Verification Commands

- Run the new backend controller-output contract RED/GREEN.
- Run the new frontend source contract RED/GREEN, typecheck and scoped ESLint.
- Run Ruff on the changed controller/test and the existing integrated static contract.
- Prove the six files are outside the bundle root, readable, visibly marked fictional, hash-bound,
  role/sequence complete, and do not mutate the bundle tree.
- Bind the exact candidate commit/tree to independent High review.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-OA-REPLY-OUTPUT-20260821-05A/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-SECOND-OA-20260821-06`
- `FPMS-DEMO-INTEGRATED-A-GRANT-20260821-07`
- `FPMS-DEMO-INTEGRATED-A-FINANCE-20260821-08`
- `FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09`
- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`

## Done Definition

Focused checks pass; six exact per-run output descriptors/files are outside and do not modify the
immutable bundle; the OA page exposes exactly the backend's six required checklist actions with no
automatic completion; independent High review reports 0/0/0.
