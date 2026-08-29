# FPMS-DEMO-V6-R2-HANDOFF-20260829-06

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["demo", "release", "documentation"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-R2-HANDOFF-20260829-06.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Publish one new immutable V6 customer-demo tag after synchronizing the active colleague Quickstart,
canonical handoff, preflight checker, and checker test to the same tag and mandatory twelve-file
attachment-role mapping.

## Explicit Non-Closure

No movement or deletion of `demo-v6-customer-20260829-r1`, no product behavior change, no evidence
model change, no database change, no rewrite of historical task records, and no default-branch merge.

## Allowed Files

- `docs/postdemo/demo-v6-colleague-clone-start-guide.md`
- `docs/postdemo/demo-v6-clone-deploy-handoff.md`
- `scripts/check_customer_demo_lifecycle_v6.py`
- `backend/tests/test_demo_integrated_a_runner.py`
- `tasks/postdemo/FPMS-DEMO-V6-R2-HANDOFF-20260829-06.md`

## Done Definition

- Both active colleague documents clone and verify `demo-v6-customer-20260829-r2`.
- Both documents direct operators to the Runbook's twelve-file attachment-role table and fixed
  file-first, role-second, confirm-last order.
- The preflight checker and focused test enforce the same tag and all twelve role mappings.
- A fresh strict V6 Stage 00–11 run passes on the final clean commit.
- The branch and new annotated `r2` tag are pushed and remote refs resolve to the final commit.
- The existing `r1` tag and historical task records remain unchanged.

## Verification Commands

- `cd backend && .venv/bin/python -m pytest -q tests/test_demo_integrated_a_runner.py`
- `backend/.venv/bin/python scripts/check_customer_demo_lifecycle_v6.py`
- `backend/.venv/bin/ruff check --no-fix scripts/check_customer_demo_lifecycle_v6.py backend/tests/test_demo_integrated_a_runner.py`
- `backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py --profile TECHNICAL_REHEARSAL --strict-ui --runs 1 --headless --artifact <fresh-path>`
- `git diff --check`

## Evidence Path

- `artifacts/FPMS-DEMO-V6-R2-HANDOFF-20260829-06/`

## Remaining Follow-Up Task IDs

- None
