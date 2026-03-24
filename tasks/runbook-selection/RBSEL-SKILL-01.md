# RBSEL-SKILL-01 — Add repo-local runbook selection skill

- Source spec: `docs/superpowers/specs/2026-03-24-runbook-selection-and-story-shape-design.md`
- Type: `repo-local skill`
- Status: `Executable`

## Closure Slice

- Exact closure slice: create a repo-local skill file that teaches agents how to classify story shape, select a runbook, and emit the minimum planning fields required by the new governance rule.
- Explicit non-closure: does not modify `AGENTS.md`, does not create the plan template, and does not implement the validation gate script.
- Remaining follow-up task ids: `RBSEL-TPL-01`, `RBSEL-GATE-01`, `RBSEL-QA-01`

## Allowlist

- `skills/fpms-runbook-selection/SKILL.md`

## Verification

- `rg -n "shared_file_density|prereq_dependency_density|be_fe_coupling|evidence_cost|chosen_runbook|Preflight Dependency Audit|Baseline Promotion Protocol|Replan Triggers" skills/fpms-runbook-selection/SKILL.md`

## Evidence

- `artifacts/RBSEL-SKILL-01/results.jsonl`
- `artifacts/RBSEL-SKILL-01/summary.md`
- `artifacts/RBSEL-SKILL-01/git/diff.patch`

