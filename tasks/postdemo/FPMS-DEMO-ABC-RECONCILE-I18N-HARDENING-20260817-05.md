# FPMS-DEMO-ABC-RECONCILE-I18N-HARDENING-20260817-05

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "frontend", "idempotency", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-RECONCILE-I18N-HARDENING-20260817-05.md
Chosen-Runbook: protected-single-lane-story

## Authority and IDs

- Customer decision: `DEC-LOCAL-DEMO-ABC-20260815`.
- Independent finding: third High review `P2-1`.
- Dependency: commit `99c7bb2`.

## Exact Closure Slice

Make the two newly introduced command-reconciliation terminal errors visible in Simplified Chinese,
while retaining the unexpected status value needed for diagnosis.

## Explicit Non-Closure

No generic error localization, page redesign, backend behavior, production, or release.

## Allowed Files

- `frontend/src/modules/demo/command-reconcile.ts`
- `frontend/tests/demo-abc-command-reconcile.mjs`
- this task card

## Verification Commands

Executable RED/GREEN message probes, Node behavior contract, frontend typecheck, scoped ESLint and
diff checks.

## Rollback

Revert the atomic commit.

## Done definition

No reconciliation error introduced by this slice renders English text in the demo UI.
