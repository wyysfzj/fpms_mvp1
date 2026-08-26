# FPMS-DEMO-V6-LEAN-EXECUTION-OVERLAY-20260826-01

Status: ACTIVE
Risk-Tier: LOW
Risk-Class: PROCESS-ONLY

## Authority and Binding

- User approval: `` `批准记录 task-scoped 精简执行 overlay` ``
- Parent plan exact commit: `80bd46829eaf5f798dda9422550a583c7fa12fde`
- Overlay: `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-lean-execution-overlay.md`
- Applicability: only parent-plan Ordinals 00–11.

## Exact Closure Slice

Record and activate the task-scoped lean-execution rules for the already approved V6 UI parity
plan. Observable outcome: the overlay is bound to the exact parent commit, preserves mandatory
invariants, defines one-pass execution/review limits, and has an explicit rollback.

## Explicit Non-Closure

No product, test, runner, API, schema, migration, runtime, evidence receipt, deployment, release,
or global-governance change. This task does not approve execution of Ordinal 00.

## Allowed Files

- `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-lean-execution-overlay.md`
- `tasks/postdemo/FPMS-DEMO-V6-LEAN-EXECUTION-OVERLAY-20260826-01.md`

## Verification Commands

```bash
test "$(git rev-parse HEAD)" = "80bd46829eaf5f798dda9422550a583c7fa12fde"
rg -n "80bd46829eaf5f798dda9422550a583c7fa12fde|批准记录 task-scoped 精简执行 overlay|Ordinal 00–11|release-last" \
  docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-lean-execution-overlay.md \
  tasks/postdemo/FPMS-DEMO-V6-LEAN-EXECUTION-OVERLAY-20260826-01.md
git diff --check
git diff --name-only | sort
```

Expected paths are exactly the two files in `Allowed Files`.

## Done Definition

- Exact parent commit and exact user approval are recorded.
- Scope, preserved invariants, liveness rule, review limit, test levels, stop conditions, and
  release-last boundary are explicit.
- Mechanical verification passes and only the two allowed files changed.
- Both files are committed together.

## Rollback

Run `git revert --no-edit <overlay-commit-sha>`. The approved parent plan remains unchanged.
