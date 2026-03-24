# RBSEL-TPL-01 — Add runbook-aware plan template

- Source spec: `docs/superpowers/specs/2026-03-24-runbook-selection-and-story-shape-design.md`
- Type: `template doc`
- Status: `Executable`

## Closure Slice

- Exact closure slice: create a reusable plan template that forces all required runbook-selection sections to appear in future multi-step plans.
- Explicit non-closure: does not modify `AGENTS.md`, does not create the repo-local skill, and does not implement any gate script logic.
- Remaining follow-up task ids: `RBSEL-GATE-01`, `RBSEL-QA-01`

## Allowlist

- `docs/templates/runbook_plan_template.md`

## Verification

- `rg -n "^## Story Shape|^## Chosen Runbook|^## Runbook Rationale|^## Preflight Dependency Audit|^## Execution Mode|^## Baseline Promotion Protocol|^## Replan Triggers|^## Atomic Task Inventory|^## Wave Plan" docs/templates/runbook_plan_template.md`

## Evidence

- `artifacts/RBSEL-TPL-01/results.jsonl`
- `artifacts/RBSEL-TPL-01/summary.md`
- `artifacts/RBSEL-TPL-01/git/diff.patch`

