# FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-DESIGN-20260822-01

Status: IMPLEMENTING
Risk-Tier: HIGH
Closure-Tags: ["customer-decision", "fee", "lifecycle", "lineage", "source-authority", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-DESIGN-20260822-01.md
Execution class: `PLANNING ONLY`
Chosen runbook: `P0-single-lane-story`

## Authority

- User request: refer to `docs/postdemo/demo-lifecycle-spec2-overlay-v3.html`, generate a new
  customer-facing demo lifecycle, and highlight changes delivered in recent weeks.
- User-approved direction: customer story line, not an internal IA checkpoint runbook.
- `docs/superpowers/specs/2026-08-21-fpms-integrated-demo-a-design.md`.
- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-FINAL-20260821-10.md` and accepted final High review.

## Exact Closure Slice

Write and independently review one concise design specification for a new customer-facing
lifecycle HTML successor. Freeze the nine-stage narrative, preservation of earlier demo
themes, recent-change highlights, source/fee/legal fail-closed wording, page structure,
content rules, and focused verification for the later HTML task.

## Explicit Non-Closure

- Do not edit `docs/postdemo/demo-lifecycle-spec2-overlay-v3.html`.
- Do not create the successor HTML in this task.
- Do not change backend, frontend, database, runtime bundle, tests, deployment, or release state.
- Do not claim official submission, patent-in-force status, configured official fees, annuity
  execution, production readiness, customer bundle activation, or product/release approval.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-DESIGN-20260822-01.md`
- `docs/superpowers/specs/2026-08-22-fpms-customer-demo-lifecycle-v5-design.md`
- `artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-DESIGN-20260822-01/**`

## Verification Commands

1. Atomic task shape:

   ```bash
   python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-DESIGN-20260822-01.md
   ```

2. Content contract:

   ```bash
   python3 scripts/check_customer_demo_lifecycle_v5_design.py --check-doc docs/superpowers/specs/2026-08-22-fpms-customer-demo-lifecycle-v5-design.md
   ```

   The implementation task may add the named checker; this planning task instead records a
   deterministic token/section probe in its evidence bundle.

3. Scope:

   ```bash
   git diff --check -- tasks/postdemo/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-DESIGN-20260822-01.md docs/superpowers/specs/2026-08-22-fpms-customer-demo-lifecycle-v5-design.md
   ```

Expected HTTP status codes: `None` (documentation-only planning task).

## Evidence Path

- `artifacts/FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-DESIGN-20260822-01/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-CUSTOMER-LIFECYCLE-V5-HTML-20260822-01`

## Done Definition

The design document is committed, binds the approved customer-facing narrative and exact
non-claims, receives an independent zero-finding spec review, and its scoped evidence is
valid. Product/runtime implementation remains untouched and the follow-up HTML task remains
open.
