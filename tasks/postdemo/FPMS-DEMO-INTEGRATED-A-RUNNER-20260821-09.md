# FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09

Status: ACTIVE
Risk-Class: PROTECTED
Outcome: Two fresh headless Integrated A rehearsals independently reach IA-18 and produce matching authoritative final states with disjoint business identities.
Dependency: Task 8 exact candidate `6eb23b1bc3d70261bc7746d33362a8cb1f4448e7`, independently APPROVED 0/0/0.

## Observable Outcome

The canonical browser journey performs a second authoritative reload at IA-18, verifies all 19
checkpoints and 12 reviewed evidence bindings, saves one final screenshot and a final checkpoint
ledger, then exits successfully. The controller runs it twice with separate run roots, databases,
storage and credentials; validates exact final lifecycle/finance state, distinct business IDs,
cleanup, redacted command metadata and artifact checksums; and writes `DIAGNOSTIC_PASS` only after
both runs satisfy the same contract.

## Non-Goals

No product behavior, finance/lifecycle semantics, input authority, security, production,
PostgreSQL, release or headed acceptance changes. No new demo workflow and no broad test suite.

## Expected Paths

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_integrated_a_runner.py`
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-RUNNER-20260821-09.md`

## Tests

- `PYTHONPATH=/private/tmp/fpms-integrated-deps.HRGhrj python3 -m pytest -q backend/tests/test_demo_integrated_a_runner.py`
- `/Users/cfcc/Library/Python/3.11/bin/ruff check scripts/run_demo_integrated_a_rehearsal.py backend/tests/test_demo_integrated_a_runner.py`
- `node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs`
- `PYTHONPATH=/private/tmp/fpms-integrated-deps.HRGhrj:backend python3 scripts/run_demo_integrated_a_rehearsal.py --artifact /tmp/fpms-integrated-a-task09 --runs 2 --headless`

## Risk and Rollback

Risk is PROTECTED because this controller accepts lifecycle and finance evidence. Rollback is the
single exact Task 9 commit and removes no business data because every run uses a disposable root.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10`
