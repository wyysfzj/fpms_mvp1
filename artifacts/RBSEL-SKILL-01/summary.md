# RBSEL-SKILL-01 Evidence Summary

- Task: `RBSEL-SKILL-01`
- Closure slice: update the minimum output template in `skills/fpms-runbook-selection/SKILL.md` so it includes `Execution Mode`, `Atomic Task Inventory`, and `Wave Plan`.
- Non-closure boundary respected: no other sections were rewritten, and no files outside the allowlist were modified.
- Verification: `rg -n "Execution Mode|Atomic Task Inventory|Wave Plan|Story Shape|Chosen Runbook|Runbook Rationale|Preflight Dependency Audit|Baseline Promotion Protocol|Replan Triggers" skills/fpms-runbook-selection/SKILL.md`
- Result: the required fields are present in both the requirements list and the minimum output template.
