# FPMS-DEMO-V6-ACCEPTANCE-COMMAND-CONTRACT-20260827-09U

Status: ACTIVE
Risk-Tier: MEDIUM
Closure-Tags: ["demo", "plan", "handoff"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-ACCEPTANCE-COMMAND-CONTRACT-20260827-09U.md
Chosen runbook: `P0-single-lane-story`

## Exact Closure Slice

Synchronize the Gate10/11 command examples with the runner and receipt comparator interfaces already
implemented and documented in the customer handoff.

## Explicit Non-Closure

No runner, comparator, receipt, product, lifecycle, fee, UI, actor evidence, deployment, or release
behavior change.

## Allowed Files

- `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-implementation.md`
- `tasks/postdemo/FPMS-DEMO-V6-ACCEPTANCE-COMMAND-CONTRACT-20260827-09U.md`

## Done Definition

Gate10 UI sessions use only actor/artifact arguments; Gate11 executes two distinct supported strict
single runs; and both comparison steps consume the generated candidate JSON path rather than a bare
SHA.
