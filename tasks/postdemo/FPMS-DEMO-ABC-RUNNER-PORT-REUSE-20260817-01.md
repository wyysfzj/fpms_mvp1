# FPMS-DEMO-ABC-RUNNER-PORT-REUSE-20260817-01

Status: READY
Risk-Tier: MEDIUM
Risk-Class: STANDARD
Closure-Tags: ["demo", "runner", "liveness", "test"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-RUNNER-PORT-REUSE-20260817-01.md

## Exact Closure Slice

Make the local ABC runner's read-only port availability probe distinguish an active listener from a
recently closed socket in `TIME_WAIT`, so a second fresh rehearsal can start immediately after a
clean first-run shutdown. Add a focused test proving the probe enables address reuse before bind and
still converts a bind failure into the existing deterministic `RuntimeError`.

## Explicit Non-Closure

No port numbers, host exposure, remote deployment, production server, retry loop, process killing,
security policy or business behavior changes.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-01`

## Allowed Files

- `backend/scripts/run_local_demo_abc.py`
- `backend/tests/test_demo_abc_local_runner.py`
- `artifacts/FPMS-DEMO-ABC-RUNNER-PORT-REUSE-20260817-01/**`

## Verification Commands

1. Focused RED/GREEN pytest for the runner port probe.
2. Existing focused local-runner tests remain green.
3. Two fresh rehearsals start sequentially without a manual wait after clean shutdown.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-RUNNER-PORT-REUSE-20260817-01/`

## Rollback

Revert this atomic commit; no database or business data migration is involved.

## Done definition

The port probe sets `SO_REUSEADDR` before bind, preserves the existing active-listener failure, and
the focused runner tests pass on the current candidate.
