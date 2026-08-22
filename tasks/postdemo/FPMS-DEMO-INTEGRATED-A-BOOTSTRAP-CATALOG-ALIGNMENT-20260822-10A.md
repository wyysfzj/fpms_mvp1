# FPMS-DEMO-INTEGRATED-A-BOOTSTRAP-CATALOG-ALIGNMENT-20260822-10A

Status: ACTIVE
Risk-Class: PROTECTED
Dependency: Final Integrated A candidate `5c636ac0781e3fbdb6b9dc09557cc64d66df7461`.

## Exact Closure Slice

The fresh local-demo bootstrap regression agrees with the already accepted Integrated A behavior:
the database contains no customer, case, generic template, or fee-rate fixtures, while the
document-template catalog contains exactly the 60 official-notice rows required by IA-03 plus the
single `OA_OUT` reply template. The test proves both the exact total and the required identities.

## Explicit Non-Closure

No runner, catalog, seed, runtime, source-authority, customer-bundle, fee, lifecycle, frontend,
deployment, security, product-wide, release, or production behavior change. Do not weaken or skip
any existing business assertion.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-BOOTSTRAP-CATALOG-ALIGNMENT-20260822-10A.md`
- `backend/tests/test_demo_abc_local_runner.py`
- `artifacts/FPMS-DEMO-INTEGRATED-A-BOOTSTRAP-CATALOG-ALIGNMENT-20260822-10A/**`

## Verification Commands

- RED: the pre-change focused bootstrap test fails because it expects `t_doc_template` to be empty
  after the accepted Integrated A catalog seed.
- GREEN: run the focused bootstrap test and the complete frozen Demo/Integrated backend set with
  only the three documented historical next-RED sentinels deselected.
- Run scoped Ruff on the modified test.
- Obtain independent High review on the exact suffix commit and final candidate.

## Evidence Path

- `artifacts/FPMS-DEMO-INTEGRATED-A-BOOTSTRAP-CATALOG-ALIGNMENT-20260822-10A/**`

## Risk and Rollback

Risk is test-contract drift around protected official-notice inputs. Rollback is this suffix commit
only. The runtime remains byte-for-byte unchanged.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-DEPLOY-PREFLIGHT-20260822-11`
