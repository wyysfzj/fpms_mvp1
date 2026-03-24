# RBSEL-QA-01 — Final close audit for runbook-selection mechanism

- Source spec: `docs/superpowers/specs/2026-03-24-runbook-selection-and-story-shape-design.md`
- Type: `qa close audit`
- Status: `Executable`

## Closure Slice

- Exact closure slice: validate that the rule, skill, template, and gate exist together as a coherent minimum mechanism, and produce a final evidence summary for story close.
- Explicit non-closure: does not modify product code or extend the mechanism beyond evidence-only close-audit corrections.
- Remaining follow-up task ids: `None`

## Allowlist

- `artifacts/RBSEL-RULE-01/**`
- `artifacts/RBSEL-SKILL-01/**`
- `artifacts/RBSEL-TPL-01/**`
- `artifacts/RBSEL-GATE-01/**`
- `artifacts/RBSEL-QA-01/**`

## Verification

- `rg -n "Story Shape Classification|chosen_runbook|Replan|planning" AGENTS.md`
- `rg -n "shared_file_density|chosen_runbook|Preflight Dependency Audit|Baseline Promotion Protocol|Replan Triggers" skills/fpms-runbook-selection/SKILL.md`
- `rg -n "^## Story Shape|^## Chosen Runbook|^## Preflight Dependency Audit|^## Baseline Promotion Protocol|^## Replan Triggers" docs/templates/runbook_plan_template.md`
- `python3 scripts/validate_plan_runbook.py docs/superpowers/plans/2026-03-24-runbook-selection-and-story-shape-implementation.md`

## Evidence

- `artifacts/RBSEL-QA-01/results.jsonl`
- `artifacts/RBSEL-QA-01/summary.md`
- `artifacts/RBSEL-QA-01/git/diff.patch`
