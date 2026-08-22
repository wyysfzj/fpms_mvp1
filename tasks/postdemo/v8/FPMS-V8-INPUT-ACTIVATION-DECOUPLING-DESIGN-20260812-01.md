# FPMS-V8-INPUT-ACTIVATION-DECOUPLING-DESIGN-20260812-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `V8 Full successor contract freeze`
Executor role: Architect / default
Risk: PROTECTED

## Design References

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/product/v8/source-decision-registry.md`
- `docs/product/v8/coverage-ledger.json`
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

No other source, test, task, manifest or shared ownership file is authorized. Preserve the
captured dirty baseline and the unrelated untracked `backend/uv.lock`.

## Verification Commands

- Content contract check recorded as `test` evidence.
- `git diff --check` over the two authored Markdown files, recorded as `lint` evidence.
- Git commit/range is the exact scope and durable checkpoint.
- One independent HIGH design review bound to commit
  `bd88cb3e38d88ef83359f4b2c70e2454bb27aeb4` and cumulative patch SHA-256
  `8f471d53690b91a222591c991c6b602cae65f827c37a8c01d3ab77578cea3b0c`.
- User written adoption on 2026-08-13.

## Git-Native Evidence

- Design commits: `20e67bf`, `d239dbd`, `bd88cb3`.
- Independent review: APPROVED; P0/P1/P2 = 0/0/0.
- No product files changed; `backend/uv.lock` remained outside every commit.

## Done Definition

The exact design and task remain within the allowlist; required content and diff checks pass; the
commit range excludes `backend/uv.lock`; an independent reviewer reports APPROVED with zero
P0/P1/P2 findings; and the user adopts the written design. These conditions are satisfied.
