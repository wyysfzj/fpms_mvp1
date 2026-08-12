# FPMS-V8-INPUT-ACTIVATION-DECOUPLING-PLAN-20260813-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `V8 Full successor implementation planning`
Executor role: Architect / default
Risk: PROTECTED

## Design References

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/product/v8/source-decision-registry.md`
- `docs/product/v8/coverage-ledger.json`
- `docs/superpowers/specs/2026-08-12-fpms-v8-input-activation-decoupling-design.md`
- Independent design review bound to commit
  `bd88cb3e38d88ef83359f4b2c70e2454bb27aeb4`, patch SHA-256
  `8f471d53690b91a222591c991c6b602cae65f827c37a8c01d3ab77578cea3b0c`.
- Customer written adoption in the current Codex thread on 2026-08-13.

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: medium
- `chosen_runbook`: `P0-multi-lane-parallel-story`

## Task Contract Profile

Task Contract Profile: `TC-DOCS`

- Verification expectation: the plan maps the approved successor design to exact task ownership,
  files, dependencies, conflict-free waves, targeted RED/GREEN commands, independent review and
  Full/Final/Release close without weakening production activation gates.

## Exact Closure Slice

Create one comprehensive executable implementation plan for the approved input-activation
decoupling design, with separate payment-workbook and service-price lanes and one serialized
Full/Final close sequence.

## Explicit Non-Closure

No product source, test, schema, migration, API, UI, manifest, catalog, task-contract or gate
ledger change. Do not implement either lane, activate production input, invent a customer value,
or change any already accepted task/evidence.

## Dependencies

- The design at `docs/superpowers/specs/2026-08-12-fpms-v8-input-activation-decoupling-design.md`
  is independently approved and customer adopted.

## Remaining Follow-Up Task IDs

- The exact execution/materialization and product tasks listed in the implementation plan.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-DECOUPLING-PLAN-20260813-01.md`
- `docs/superpowers/plans/2026-08-13-fpms-v8-input-activation-decoupling.md`

No other file is authorized. Preserve the unrelated untracked `backend/uv.lock`.

## Verification Commands

- Plan content/dependency/file-conflict assertions recorded as `test` evidence.
- `git diff --check` over the exact two Markdown files recorded as `lint` evidence.
- Git commit/range is the exact scope and durable checkpoint.
- One independent HIGH plan review bound to commit
  `0d079647d7619a32ad1e6743ef004627702470ac` and cumulative patch SHA-256
  `193fb703aefa7b96f44bb7586e771cccab42d4d615d1f0e87aa9e7b18839fbe3`.

## Git-Native Evidence

- Plan commits: `7392e5f`, `6d2e195`, `0d07964`.
- Independent review: APPROVED; P0/P1/P2 = 0/0/0.
- No product files changed; `backend/uv.lock` remained outside every commit.

## Done Definition

The plan is complete, executable and conflict-aware; all targeted checks pass; its exact commit
range excludes `backend/uv.lock`; and an independent reviewer reports APPROVED with zero
P0/P1/P2. These conditions are satisfied.
