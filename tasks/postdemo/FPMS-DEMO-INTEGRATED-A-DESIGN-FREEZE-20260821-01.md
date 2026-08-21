# FPMS-DEMO-INTEGRATED-A-DESIGN-FREEZE-20260821-01

Status: REVIEW
Risk-Class: PROTECTED
Risk-Tier: HIGH
Closure-Tags: ["customer-decision", "demo", "lifecycle", "lineage", "fee", "payment"]
Task-Path: tasks/postdemo/FPMS-DEMO-INTEGRATED-A-DESIGN-FREEZE-20260821-01.md
Role: Design architect
Outcome: freeze the customer-approved single-case successor that combines the complete prior V7
demo journey with the accepted local ABC runtime-input and customer-finance journey.

## Authority

- `AGENTS.md` and the active governance manifest/modules.
- `docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md`.
- `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`.
- `docs/product/v8/customer-decisions/2026-08-21-integrated-demo-a.txt`.
- Customer confirmation in the current Codex task: the upcoming demo must cover both the prior
  demo and the new changes, followed by exact confirmation `确认方案A`.

## Exact closure

Create one successor design that freezes:

1. one fictional client and one fictional case for the entire presentation;
2. every prior V7 customer-visible capability: client/contact, case, wizard/catalog boundary,
   filing preparation, first OA, OA_OUT, invalid and valid receipt behavior, independent later OA,
   grant notice, grant-source replacement and superseded-task fail-closed behavior;
3. the accepted ABC successor: immutable runtime bundle, service obligation and locked draft,
   unique AR bill, bank receipt and full offset;
4. one ordered checkpoint ledger, exact observable states, error/no-write rules, two-run headed
   acceptance, independent High review and evidence/cleanup requirements;
5. the explicit correction that no missing official-fee authority, hard-coded historical amount,
   seed, enrichment or fixture may be used to make the combined journey appear complete.

## Explicit non-closure

No backend, frontend, test, schema, migration, seed or runner implementation. No actual runtime
bundle contents or customer/source activation. No official fee/payment truth, production,
PostgreSQL, remote deployment, security remediation, broad/product/release gate or release claim.

## Allowed files

- `tasks/postdemo/FPMS-DEMO-INTEGRATED-A-DESIGN-FREEZE-20260821-01.md`
- `docs/product/v8/customer-decisions/2026-08-21-integrated-demo-a.txt`
- `docs/product/v8/source-decision-registry.md`
- `docs/superpowers/specs/2026-08-21-fpms-integrated-demo-a-design.md`
- `artifacts/FPMS-DEMO-INTEGRATED-A-DESIGN-FREEZE-20260821-01/**`

## Verification

- Preserve the exact two customer messages, byte size and SHA-256 in the decision registry.
- Assert that the design maps `V7-01` through `V7-14` into the successor and contains the ABC
  runtime bundle, service draft, unique bill, bank receipt, offset, two fresh headed runs,
  independent High review, rollback and non-closure boundary.
- `git diff --check` over the exact allowlist.
- Confirm no changed path falls outside the allowlist.
- Obtain one independent specification review with P0/P1/P2 = 0/0/0 before implementation
  planning.

## Follow-up

- Materialize an ordered implementation plan only after this written design is accepted.
- Split every discovered implementation defect into one exact atomic task; do not absorb it into
  the design task.

## Rollback

Revert only the exact design commit. No business data, runtime source or prior accepted ABC
implementation is changed by this task.

## Done definition

The four non-artifact allowlisted files are complete and internally consistent, the task evidence
is valid, the exact design commit has independent zero-finding review, and the customer has
accepted the written successor design. Until then this task remains `REVIEW`.
