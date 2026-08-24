# FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-DESIGN-20260825-06A

Status: ACTIVE
Risk-Tier: HIGH
Closure-Tags: ["fee", "source-authority", "runtime-input", "seed"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-DESIGN-20260825-06A.md
Execution class: `PLANNING ONLY`

## Authority

- User approval on 2026-08-25: `批准 runtime 官费来源最小架构整改边界`.
- Approved V6 design:
  `docs/superpowers/specs/2026-08-23-fpms-demo-v6-dual-track-fee-enrichment-design.md`.
- Reproduced canonical rehearsal failure:
  `DEMO_GOV_RATE_SOURCE_CONFLICT` at stage 07 on a fresh database because the runtime bundle
  selected official-fee digests but the local runner had no corresponding rate-book facts to
  materialize.

## Exact Closure Slice

Freeze and independently review one short design delta that makes the V6 runtime bundle the complete,
digest-bound carrier for exactly one official rate book and its selected fee rows. The design must
define loader cross-validation, fresh-run materialization, customer/synthetic authority boundaries,
failure conditions, and the smallest implementation/test allowlist.

## Explicit Non-Closure

- Do not edit product code, tests, runner behavior, database schema, migrations, demo documents, or
  generated evidence in this design task.
- Do not build a generic rate-book importer, rule engine, network fetcher, admin UI, production seed,
  fee-reduction path, or new official-fee calculation.
- Do not invent a CNIPA source, amount, effective date, approval, activation, or customer decision.
- Do not change V6 stages, fee codes, preview/confirmation semantics, GOV/SERVICE separation, or
  previously completed lifecycle behavior.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-DESIGN-20260825-06A.md`
- `docs/superpowers/specs/2026-08-25-fpms-demo-v6-runtime-official-source-design.md`
- `artifacts/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-DESIGN-20260825-06A/**`

## Verification Commands

1. Atomic task shape:

   ```bash
   python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-DESIGN-20260825-06A.md
   ```

2. Scoped document check:

   ```bash
   git diff --check 9e739a76fe5e454440fc414ad84ad9cc783e0818^..HEAD -- tasks/postdemo/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-DESIGN-20260825-06A.md docs/superpowers/specs/2026-08-25-fpms-demo-v6-runtime-official-source-design.md
   ```

3. Independent review of the committed design must report `APPROVED` with P0/P1/P2 = 0/0/0.

Expected HTTP status codes: `None` (documentation-only design task).

## Evidence Path

- `artifacts/FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-DESIGN-20260825-06A/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-RUNTIME-OFFICIAL-SOURCE-20260825-06B`

## Done Definition

The committed delta specification is independently approved, presents no broader alternative than
the minimum inline runtime-source contract, and is ready for explicit user review. No runtime
implementation occurs in this task.
