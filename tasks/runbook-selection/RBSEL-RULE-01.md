# RBSEL-RULE-01 — Add mandatory story-shape and runbook rule to `AGENTS.md`

- Source spec: `docs/superpowers/specs/2026-03-24-runbook-selection-and-story-shape-design.md`
- Type: `repo governance doc`
- Status: `Executable`

## Closure Slice

- Exact closure slice: add a mandatory `AGENTS.md` rule section that requires story-shape classification, `chosen_runbook` recording in spec and plan, and replanning when new shared prerequisites are discovered.
- Explicit non-closure: does not create the repo-local skill, plan template, validation script, or any product feature code.
- Remaining follow-up task ids: `RBSEL-SKILL-01`, `RBSEL-TPL-01`, `RBSEL-GATE-01`, `RBSEL-QA-01`

## Allowlist

- `AGENTS.md`

## Verification

- `rg -n "Story Shape Classification|chosen_runbook|Replan|planning" AGENTS.md`

## Evidence

- `artifacts/RBSEL-RULE-01/results.jsonl`
- `artifacts/RBSEL-RULE-01/summary.md`
- `artifacts/RBSEL-RULE-01/git/diff.patch`

