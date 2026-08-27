# FPMS-DEMO-V6-UI-PARITY-LOCAL-CREDENTIAL-HANDOFF-20260827-08AQ

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["demo", "security"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-LOCAL-CREDENTIAL-HANDOFF-20260827-08AQ.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Make the setup-only local UI session usable by showing its per-run `admin` credential only on the
interactive terminal stderr while retaining redacted stdout and excluding the credential from all
artifact, receipt, screenshot, and persisted observer bytes.

## Explicit Non-Closure

No fixed/default password, production credential, reviewer credential disclosure, browser auto-login,
authentication bypass, permission change, credential persistence, generic secret-management work,
Task 09 docs, or release change.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-LOCAL-CREDENTIAL-HANDOFF-20260827-08AQ.md`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_v6_ui_session.py`

## Verification

Focused finalized UI-session test, full UI-session/runner focused set, scoped Ruff, diff check, and
independent HIGH review.

## Done Definition

The operator can enter the normal login page with the current one-time password; stdout and all
persisted evidence remain redacted; the reviewer password is never shown.
