# FPMS-DEMO-V6-UI-PARITY-CONTRACT-20260826-01

Status: IMPLEMENTED / PENDING INDEPENDENT REVIEW
Risk-Tier: HIGH
Closure-Tags: ["data", "fee", "lifecycle", "lineage", "source-authority", "ui"]
Task-Path: tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-CONTRACT-20260826-01.md
Chosen runbook: `P0-prereq-heavy-story`

## Design References

- Approved design:
  `docs/superpowers/specs/2026-08-26-fpms-demo-v6-ui-parity-design.md`, exact commit
  `5d48d0aed4356e7a1bd2d958301afe6ffab12b4d`.
- Approved implementation plan:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-implementation.md`, exact commit
  `80bd46829eaf5f798dda9422550a583c7fa12fde`.
- Active lean overlay:
  `docs/superpowers/plans/2026-08-26-fpms-demo-v6-ui-parity-lean-execution-overlay.md`.
- Ordinal 00 accepted commit: `63ecda4061a3705fad2d7ddc1c4c256c01c2c49e`.

## Exact Closure Slice

Create the single versioned `fpms.demo-v6-ui-parity/v1` machine-readable contract and its
standalone Node validator. The contract materializes every stage 01–11 input, source binding,
visible output, normal UI route/control/evidence point, normalization rule, required 07–11
authority assertion, top-level candidate/bundle/actor/run binding, and the exact allowed-difference
whitelist frozen in design sections 3.1 and 7.

## Fixed Scope Decision

- `shared_file_density=LOW`
- `prereq_dependency_density=HIGH`
- `be_fe_coupling=NONE`
- `evidence_cost=LOW`
- `chosen_runbook=P0-prereq-heavy-story`
- Scope expansion is denied; a missing approved field or contradictory design rule stops the task.

## Exact Behavior

1. The JSON schema id is exactly `fpms.demo-v6-ui-parity/v1`; actors are exactly `HUMAN`, `CODEX`,
   and `STRICT_UI_TECHNICAL`.
2. Every input row fixes `stage`, `field_key`, `classification`, `value_rule`, `ui_route`, `control`,
   `source_selector`, `normalization`, and `required=true`.
3. Every output row also fixes `observable`, `expected_rule`, and its UI evidence point.
4. Classifications are only `EXPLICIT_INPUT`, `SOURCE_BOUND`, and `APP_GENERATED`; business dates,
   amounts, reasons, source digests, and statuses are never allowed differences.
5. Allowed differences are exactly run suffix, UUID/autoincrement IDs, database/file paths, dynamic
   credentials, idempotency keys, and system timestamps.
6. Every semicolon-separated Stage 07–11 strict-receipt condition in design section 7 is an
   independent named `required=true` assertion; no collapsed aggregate boolean or free text.
7. The validator accepts the canonical contract and rejects named fixtures for a missing field,
   duplicate field, wrong classification, unknown allowed difference, and collapsed Stage 07–11
   assertion. It also rejects unknown object keys and stage/route/control drift.

## Explicit Non-Closure

- No backend, frontend, runner, Playwright journey, UI, API, schema, migration, seed, runtime source,
  business behavior, run receipt, or customer/release activation change.
- No second contract version, general schema framework, generated types, generic validator library,
  adjacent fixture cleanup, or Ordinal 02 implementation.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-V6-UI-PARITY-CONTRACT-20260826-01.md`
- `FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs`
- `artifacts/FPMS-DEMO-V6-UI-PARITY-CONTRACT-20260826-01/**`

## Verification Commands

```bash
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs
git diff --check
```

RED must name and reject each required invalid fixture before the canonical contract exists. GREEN
must accept the canonical file, prove exact stage coverage 01–11 and independent 07–11 assertion
coverage, and reject every negative fixture. Independent review binds the exact commit and proves
no product-file diff.

Expected HTTP status codes: none; this is a data-contract and standalone-validator task.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-UI-PARITY-CONTRACT-20260826-01/**`

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-UI-PARITY-SESSION-20260826-02`, blocked until this task is independently accepted.

## Done Definition

The canonical contract and standalone validator close the exact approved field/assertion matrix;
the named RED fixtures fail for their intended reasons; canonical GREEN, scope, evidence, and one
independent exact-commit review pass with `P0/P1/P2 = 0/0/0`; no non-closure item is absorbed.

## Rollback

Run `git revert --no-edit <exact-task-sha>`. This removes only the contract, validator, and task
card; Ordinal 00 remains accepted.
