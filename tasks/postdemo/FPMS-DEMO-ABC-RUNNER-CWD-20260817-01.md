# FPMS-DEMO-ABC-RUNNER-CWD-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "runner", "migration"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-RUNNER-CWD-20260817-01.md

## Exact Closure Slice

Make the local ABC runner resolve Alembic's script directory from its own backend root rather than
the caller's current working directory. Add a regression test that changes cwd outside `backend/`
and still completes a fresh migration/bootstrap.

## Explicit Non-Closure

No production PostgreSQL migration remediation, generic Alembic configuration change, runner redesign,
cleanup policy change, browser work, security or release.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-01`

## Allowed Files

- `backend/scripts/run_local_demo_abc.py`
- `backend/tests/test_demo_abc_local_runner.py`
- `artifacts/FPMS-DEMO-ABC-RUNNER-CWD-20260817-01/**`

## Verification Commands

1. RED reproduces the exact root-cwd `Path doesn't exist: alembic` failure.
2. GREEN changes cwd outside backend and completes bootstrap.
3. Existing runner focused test and Ruff pass.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-RUNNER-CWD-20260817-01/`

## Rollback

Revert the atomic implementation commit.

## Done definition

The documented root-level runner command is cwd-independent for its Alembic lookup. Independent High
acceptance remains required.
