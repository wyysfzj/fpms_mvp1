# RBSEL-SKILL-01 Evidence Summary

- Task: add a repo-local runbook selection skill instruction that forces reading the current story background and existing constraints before classification/output rules.
- Modified file: `skills/fpms-runbook-selection/SKILL.md`
- Verification: `rg -n "First Pass|current story background|existing constraints|classification or output-format rules" skills/fpms-runbook-selection/SKILL.md`
- Result: passed, with the new instruction present at the top of the skill body.
