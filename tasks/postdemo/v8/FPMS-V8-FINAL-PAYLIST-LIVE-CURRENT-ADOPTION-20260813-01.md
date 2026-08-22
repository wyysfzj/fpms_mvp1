# FPMS V8 Final PayList Live Current Adoption

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Exact Closure Slice

Adopt approved commit `5065900d6355e39bd5817af4ef895a5c7add6581`: its exact two paths
plus this task, focused contract and adoption story, exactly five fingerprint paths.

## Explicit Non-Closure

No existing product/test/task byte change; no ledger row/Row283/report/release claim. Production
remains CONFIG_REQUIRED/PENDING/409 NO WRITE; TEST_ONLY remains isolated.

## Allowed Files

- exact two source paths; this task; `backend/tests/test_v8_final_paylist_live_adoption.py`;
  `docs/product/v8/stories/V8-FINAL-PAYLIST-LIVE-CURRENT-ADOPTION.md`; reviewer receipt; sole ledger.

## Verification Commands

- focused pytest, Ruff/format, JSON/diff/tree/ledger patch; independent 0/0/0 receipt then ledger.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FINAL-CLOSE-20260712-01`

## Evidence Path

- `/tmp/fpms-v8-final-close-20260813/paylist_real_e2e.log`
