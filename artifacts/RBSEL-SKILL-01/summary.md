# RBSEL-SKILL-01 Evidence Summary

- Task: `RBSEL-SKILL-01`
- Role: worker
- Closure slice: create the repo-local skill file that teaches agents how to classify story shape, select a runbook, and emit the minimum planning fields required by the governance rule.
- Non-closure boundary respected: no changes to `AGENTS.md`, no plan template creation, no validation gate script implementation.

## Modified Files

- `skills/fpms-runbook-selection/SKILL.md`

## Verification

- Ran: `rg -n "shared_file_density|prereq_dependency_density|be_fe_coupling|evidence_cost|chosen_runbook|Preflight Dependency Audit|Baseline Promotion Protocol|Replan Triggers" skills/fpms-runbook-selection/SKILL.md`
- Result: passed with matches for all required terms.

## Evidence Artifacts

- `artifacts/RBSEL-SKILL-01/results.jsonl`
- `artifacts/RBSEL-SKILL-01/summary.md`
- `artifacts/RBSEL-SKILL-01/git/diff.patch`

## Notes

- The diff patch is scoped to the new repo-local skill file only.
- No product code, templates, scripts, or AGENTS.md were edited.
