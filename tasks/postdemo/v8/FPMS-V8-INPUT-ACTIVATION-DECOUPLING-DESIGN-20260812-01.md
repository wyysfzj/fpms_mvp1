# FPMS-V8-INPUT-ACTIVATION-DECOUPLING-DESIGN-20260812-01

Status: IMPLEMENTING
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `V8 Full successor contract freeze`
Executor role: Architect / default
Repository risk: HIGH

## Design References

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/execution.md`
- `docs/agents/evidence.md`
- `docs/agents/domain-safety.md`
- `docs/agents/source-authority.md`
- `docs/product/v8/source-decision-registry.md`
- `docs/product/v8/catalog.frozen.json`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- Customer decision in the current Codex thread on 2026-08-12: the clean official payment
  workbook and the approved complete service-price version are user inputs; their absence must
  not prevent implementation of the corresponding capabilities.

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-DOCS`

- Verification expectation: the written successor design distinguishes capability readiness from
  production-input activation, preserves all fee/source/lineage fail-closed rules, maps every
  affected catalog row, freezes test-fixture isolation and defines Full/Final/Release behavior.

## Exact Closure Slice

Freeze one successor design for rows 175, 176, 214–229 and 278 that permits development and
independent acceptance with isolated test-only inputs while requiring real reviewed user inputs
before production activation, formal workbook generation or service receivable creation. Freeze
the corresponding Full/Final/Release interpretation and the three exact workbook-input successor
owner contracts without changing the frozen catalog here.

## Explicit Non-Closure

No product source, test, schema, migration, API, UI, manifest, catalog, gate ledger, source
registry or existing task-contract change. Do not activate either production lane, fabricate a
customer input, weaken a 409/no-write boundary, or claim compatibility with an unavailable real
workbook or price version.

## Dependencies

- Current Scheme A customer decisions are adopted.
- V8 Inventory and Foundation are terminal PASS.
- No real payment workbook or approved complete service-price version is required for this
  design-only task.

## Remaining Follow-Up Task IDs

- `FPMS-V8-INPUT-ACTIVATION-DECOUPLING-IMPLEMENTATION-PLAN-20260812-01`
- `FPMS-V8-PAYMENT-WORKBOOK-INPUT-VERSION-CARRIER-20260812-01`
- `FPMS-V8-PAYMENT-WORKBOOK-INPUT-GOVERNANCE-SERVICE-20260812-01`
- `FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01`
- Exact successor materialization tasks identified by that plan.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-DECOUPLING-DESIGN-20260812-01.md`
- `docs/superpowers/specs/2026-08-12-fpms-v8-input-activation-decoupling-design.md`
- `artifacts/FPMS-V8-INPUT-ACTIVATION-DECOUPLING-DESIGN-20260812-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Preserve the
captured dirty baseline and the unrelated untracked `backend/uv.lock`.

## Verification Commands

- Content contract check recorded as `test` evidence.
- `git diff --check` over the two authored Markdown files, recorded as `lint` evidence.
- Baseline-subtracted exact allowlist audit, recorded as `scope` evidence.
- One independent HIGH design review bound to the exact patch.
- Repository task gate and atomic evidence validation after independent approval.

## Evidence Path

- `artifacts/FPMS-V8-INPUT-ACTIVATION-DECOUPLING-DESIGN-20260812-01/**`

## Done Definition

The exact design and task remain within the allowlist; required content and diff checks pass; the
baseline-subtracted patch excludes `backend/uv.lock`; an independent reviewer reports APPROVED
with zero P0/P1/P2 findings; task gate and atomic evidence validation pass. Only then may this
design task be reported PASS.
