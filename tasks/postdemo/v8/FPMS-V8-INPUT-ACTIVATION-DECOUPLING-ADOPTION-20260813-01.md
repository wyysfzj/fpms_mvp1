# FPMS-V8-INPUT-ACTIVATION-DECOUPLING-ADOPTION-20260813-01

Status: IMPLEMENTATION CANDIDATE
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Implementer / default
Risk: PROTECTED
Task Contract Profile: `TC-DOCS`
Customer written adoption: 2026-08-13

## Authority

- Independently approved design commit:
  `bd88cb3e38d88ef83359f4b2c70e2454bb27aeb4`.
- Reviewed cumulative design patch SHA-256:
  `8f471d53690b91a222591c991c6b602cae65f827c37a8c01d3ab77578cea3b0c`.
- Current scope: rows 175, 176, 214-229, 278, 281-283.

## Exact Closure Slice

Adopt the successor authority, create the four executable successor cards, and append the
latest-wins development-versus-production prerequisite interpretation to exactly the 22 existing
task cards named by the approved plan.

## Explicit Non-Closure

No product code, lane manifest, frozen catalog, coverage ledger, schema, migration, production
input, positive gate decision, or production activation. Existing task closure, non-closure,
allowlist, permissions, tests, and evidence remain unchanged.

## Dependency Interpretation

- Development may reach `CAPABILITY_READY` with isolated `TEST_ONLY` inputs.
- Missing reviewed real input is `CONFIG_REQUIRED`; production action is `409 / NO WRITE`.
- `DG-PAYMENT-WORKBOOK:GLOBAL` and `DG-SERVICE-RATE-VERSION:GLOBAL` remain production gates.
- Payment order:
  `FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01 (row175) -> WB-I1 -> row214 -> WB-I2 -> WB-I3 -> rows215-222 -> row278`.
- Row 175 remains exactly 11 members and row 176 remains exactly 8 members. WB-I1/WB-I2/WB-I3
  are external prerequisites, never lane-manifest members.
- Full/Final/Release may accept `CONFIG_REQUIRED` only with negative-path evidence and never
  claims production activation.

## Allowed Files

- This task card.
- `docs/product/v8/reviews/V8-INPUT-ACTIVATION-DECOUPLING-CURRENT-ADOPTION.md`.
- The four successor task cards named by this adoption.
- `backend/tests/test_v8_input_activation_decoupling_contract.py`.
- Exactly the 22 existing task cards named in plan section 5.

## Verification

- Focused RED/GREEN pytest for the adoption contract.
- Scoped Ruff on the focused Python test.
- Exact owned-path `git diff --check`.
- SHA-256 verification that `docs/product/v8/catalog.frozen.json` remains unchanged.
- Git-native scope evidence; do not use legacy taskctl or artifact/evidence machinery.

## Evidence Path

- Exact Git commit/range plus the reported RED/GREEN, Ruff, exact diff, frozen-hash, scope, and
  independent-review results. No legacy artifact directory is created.

## Independent Close

This PROTECTED adoption requires an independent zero-finding review of the exact commit before it
can be accepted. The implementer does not approve its own work. This candidate never claims production activation.
