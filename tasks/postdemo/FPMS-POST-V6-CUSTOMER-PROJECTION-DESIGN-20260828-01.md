# FPMS-POST-V6-CUSTOMER-PROJECTION-DESIGN-20260828-01

Status: READY / CONTRACT FROZEN
Risk-Tier: HIGH
Closure-Tags: ["fee", "lifecycle", "lineage", "ui"]
Task-Path: tasks/postdemo/FPMS-POST-V6-CUSTOMER-PROJECTION-DESIGN-20260828-01.md
Chosen runbook: `P0-frontend-heavy-story`

## Authority and observed defects

- User direction on 2026-08-28: design and plan the two approved customer-facing remediation
  recommendations on branch `codex/post-v6-mainpath-20260828`.
- Current case stage is authorization registration, while the case document tab presents the
  initial-filing material gate as a current-node blocker.
- The case fee tab and expanded three-track history expose raw UUIDs, hashes, lineage keys,
  fee/status codes, ISO timestamps, and duplicated gate codes as primary customer content.

## Exact Closure Slice

Write one implementation-ready design for the minimum customer projection remediation:

1. make the initial-filing document gate's stage applicability explicit without changing its
   underlying requirements or fabricating PASS;
2. present fee obligations as Chinese business summaries while retaining raw audit identifiers
   behind an explicit disclosure;
3. apply the same customer-versus-audit hierarchy to the expanded document/evidence and fee
   history lanes, including safe enum fallback, date formatting, and stable deduplication;
4. freeze focused verification and stop conditions for the later implementation plan.

## Allowed Files

- `tasks/postdemo/FPMS-POST-V6-CUSTOMER-PROJECTION-DESIGN-20260828-01.md`
- `docs/superpowers/specs/2026-08-28-post-v6-customer-projection-remediation-design.md`
- `artifacts/FPMS-POST-V6-CUSTOMER-PROJECTION-DESIGN-20260828-01/**`

## Explicit Non-Closure

- No product source, test, API, schema, database, seed, runbook, demo state, or evidence fact
  modification.
- No lifecycle transition, legal status, fee amount, fee source, payment state, document lineage,
  permission, or filing-gate requirement change.
- No generic rules engine, backend gate-framework redesign, new request, new persistence, broad UI
  cleanup, or unrelated English-text remediation.
- No modification or absorption of the existing untracked
  `docs/postdemo/demo-v6-colleague-clone-start-guide.md`.
- No implementation plan before the written design passes independent review and the user approves
  the reviewed design.

## Verification Commands

1. `git diff --check -- tasks/postdemo/FPMS-POST-V6-CUSTOMER-PROJECTION-DESIGN-20260828-01.md docs/superpowers/specs/2026-08-28-post-v6-customer-projection-remediation-design.md`
2. Verify the design contains no unresolved `TODO`, `TBD`, or placeholder text.
3. Independent spec-document review with `Approved` status.
4. Finalize baseline-subtracted scope evidence and run the task gate.

## Evidence Path

`artifacts/FPMS-POST-V6-CUSTOMER-PROJECTION-DESIGN-20260828-01/`

## Remaining Follow-Up Task IDs

- `FPMS-POST-V6-CUSTOMER-PROJECTION-PLAN-20260828-01`
- Product implementation task ID to be frozen by the approved implementation plan.
