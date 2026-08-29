# FPMS-DEMO-V6-FINAL-CANDIDATE-CLOSE-20260829-04

## Exact Closure Slice

- Freeze the current V6 demo branch HEAD as the final local candidate.
- Run the canonical checker, 103/30/11 contract, runner tests, Ruff, diff check, and one fresh strict Stage 00–11 UI run at that exact HEAD.
- Push the branch without force and publish immutable tag `demo-v6-customer-20260829-r1` at the verified candidate commit.
- Fresh-clone that tag, confirm exact tag and clean state, install from lock/package metadata, and repeat the canonical checks plus strict Stage 00–11 UI run.
- Record exact commands and results without claiming HUMAN or independent CODEX acceptance.

## Explicit Non-Closure

- Do not create, prewrite, copy, or impersonate HUMAN or independent CODEX receipts.
- Do not run the actor comparator until both external receipts actually exist for this exact candidate.
- Do not change product code, business facts, V6 contracts, docs, tags after verification, or remote history.
- Do not force-push, move an existing tag, merge to remote `master`, deploy production, or weaken a failed gate.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-ACTOR-RECEIPTS-20260826-10`
- `FPMS-DEMO-V6-UI-PARITY-CANDIDATE-CLOSE-20260826-11`

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-FINAL-CANDIDATE-CLOSE-20260829-04.md`

## Verification Commands

- `backend/.venv/bin/python scripts/check_customer_demo_lifecycle_v6.py`
- `node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs`
- `(cd backend && .venv/bin/python -m pytest -q tests/test_demo_integrated_a_runner.py)`
- `backend/.venv/bin/ruff check --no-fix scripts/check_customer_demo_lifecycle_v6.py backend/tests/test_demo_integrated_a_runner.py`
- `git diff --check`
- `backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py --profile TECHNICAL_REHEARSAL --strict-ui --runs 1 --headless --artifact <fresh-path>`
- Repeat canonical and strict checks in a fresh clone of the immutable tag.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-FINAL-CANDIDATE-CLOSE-20260829-04/`

