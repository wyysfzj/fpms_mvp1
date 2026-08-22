# FPMS-DEMO-ABC-FRESH-LOCAL-RUNNER-20260816-01

Status: READY
Risk-Class: PROTECTED
Closure-Tags: ["demo", "sqlite", "seed", "local-runner"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-FRESH-LOCAL-RUNNER-20260816-01.md

## Story shape

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: startup-only
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Design references

- `AGENTS.md`
- `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`
- `docs/superpowers/plans/2026-08-16-fpms-local-demo-abc-fast-track.md`
- `tasks/postdemo/FPMS-DEMO-ABC-BUNDLE-PREFLIGHT-20260816-01.md`

## Exact Closure Slice

Add one local screen-share runner that validates the runtime bundle and required environment before
creating a unique run directory, then migrates a fresh SQLite database, seeds only roles plus two
distinct demo users, and can start loopback API/Vite processes. Invalid input creates no run
directory, database or listener. Reusing a run ID fails closed.

## Explicit Non-Closure

No Docker/production deployment, security remediation, customer/case/lifecycle fixture,
template/rate persistence, business object enrichment, billing behavior, frontend feature or
actual customer bundle. The runner does not install dependencies or delete failed run evidence.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-RUNTIME-SERVICE-DRAFT-20260816-01`
- `FPMS-DEMO-ABC-UNIQUE-AR-BILL-20260816-01`
- `FPMS-DEMO-ABC-PAYMENT-OFFSET-20260816-01`
- `FPMS-DEMO-ABC-FINANCE-UI-20260816-01`
- `FPMS-DEMO-ABC-LIVE-E2E-20260816-01`

## Allowed Files

- `backend/scripts/seed_demo_abc.py`
- `backend/scripts/run_local_demo_abc.py`
- `backend/tests/test_demo_abc_local_runner.py`
- `artifacts/FPMS-DEMO-ABC-FRESH-LOCAL-RUNNER-20260816-01/**`

## Verification Commands

1. RED proves the runner/seed do not exist.
2. Target pytest proves invalid bundle no-write, fresh migration, exactly two demo users, no
   customer/case/template/fee business fixtures, and duplicate run-ID rejection.
3. Scoped Ruff passes.
4. Bootstrap-only smoke on a unique run ID returns 0 and creates a migrated SQLite DB; cleanup
   moves only that exact run directory after evidence capture.
5. Exact allowlist and `git diff --check` pass. No broad/release gate runs.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-FRESH-LOCAL-RUNNER-20260816-01/`

## Rollback

Revert the atomic story commit. Existing per-run temporary evidence remains untouched.

## Done definition

Target checks pass and the exact commit is ready for independent High review. Only local demo
bootstrap capability is claimed.
