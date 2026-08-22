# FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-PLAN-20260822-01

Status: IMPLEMENTING
Risk-Tier: HIGH
Closure-Tags: ["customer-decision", "fee", "lifecycle", "lineage", "source-authority", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-PLAN-20260822-01.md
Execution class: `PLANNING ONLY`
Chosen runbook: `P0-single-lane-story`

## Authority

- User-approved written design:
  `docs/superpowers/specs/2026-08-22-fpms-customer-demo-lifecycle-v5-design.md`.
- Independent spec review with `APPROVED` and `P0/P1/P2 = 0/0/0`.

## Exact Closure Slice

Write and independently review one minimal implementation plan for the standalone customer
Lifecycle V5 HTML successor. The plan must materialize exactly one later implementation task,
one new HTML file, one lightweight deterministic checker, focused visual verification, one
commit, and one independent High review.

## Explicit Non-Closure

- Do not create or edit the successor HTML or checker in this planning task.
- Do not edit the V3 reference page, product runtime, database, tests, deployment, or release.
- Do not absorb governance activation remediation into the HTML task.
- Do not activate customer templates, official fees, annuity data, or production claims.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-PLAN-20260822-01.md`
- `docs/superpowers/plans/2026-08-22-fpms-customer-demo-lifecycle-v5.md`
- `artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-PLAN-20260822-01/**`

## Verification Commands

1. Atomic task shape:

   ```bash
   python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-PLAN-20260822-01.md
   ```

2. Plan contract:

   ```bash
   python3 -c 'from pathlib import Path; s=Path("docs/superpowers/plans/2026-08-22-fpms-customer-demo-lifecycle-v5.md").read_text(); assert "one atomic HTML task" in s; assert "governance activation" in s; assert "demo-lifecycle-customer-v5.html" in s'
   ```

3. Scope:

   ```bash
   git diff --check -- tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-PLAN-20260822-01.md docs/superpowers/plans/2026-08-22-fpms-customer-demo-lifecycle-v5.md
   ```

Expected HTTP status codes: `None` (documentation-only planning task).

## Evidence Path

- `artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-PLAN-20260822-01/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01`

## Done Definition

The committed plan is implementation-ready, keeps the execution to one atomic HTML task,
preserves all design non-claims, records the governance preflight stop condition, and receives
an independent zero-finding plan review. No HTML or runtime implementation occurs.
