# RBSEL-SKILL-01 Evidence Summary

- Task: add a repo-local runbook selection skill instruction that forces reading the current story background and existing constraints before classification/output rules, and make `P0-prereq-heavy-story` mandatory when shared prerequisites must be frozen first.
- Modified file: `skills/fpms-runbook-selection/SKILL.md`
- Verification: `rg -n 'First Pass|When To Use|Required Story Shape Classification|Runbook Families|Selection Rules|P0-prereq-heavy-story|Preflight Dependency Audit|Baseline Promotion Protocol|Replan Triggers|Recommended Execution Mode|Minimum Output Template' /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/.worktrees/rbsel-skill-01/skills/fpms-runbook-selection/SKILL.md`
- Result: passed, with the full skill closure slice present and the prereq-heavy selection rule made enforceable.
