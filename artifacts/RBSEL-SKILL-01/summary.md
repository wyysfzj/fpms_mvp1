# RBSEL-SKILL-01 Evidence Summary

- Task: add a repo-local runbook selection skill instruction that forces reading the current story background and existing constraints before classification/output rules, and make `P0-prereq-heavy-story` an exclusive override when shared prerequisites must be frozen first.
- Modified file: `skills/fpms-runbook-selection/SKILL.md`
- Baseline: `34a34a9`
- Verification: `rg -n 'shared_file_density|prereq_dependency_density|be_fe_coupling|evidence_cost|chosen_runbook|Preflight Dependency Audit|Baseline Promotion Protocol|Replan Triggers' skills/fpms-runbook-selection/SKILL.md`
- Result: passed, with the full task baseline-to-current diff captured in `artifacts/RBSEL-SKILL-01/git/diff.patch` and the prereq-heavy selection rule made exclusive and enforceable.
