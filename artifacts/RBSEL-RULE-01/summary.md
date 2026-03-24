# RBSEL-RULE-01 Evidence Summary

- Scope: updated the `AGENTS.md` runbook-selection rule so `Story Shape Classification` is required in both the task spec and the task plan.
- Verification: `rg -n "Story Shape Classification|chosen_runbook|Replan|planning" AGENTS.md`
- Result: the rule now explicitly says the task spec and the task plan both record `Story Shape Classification`, and both record `chosen_runbook`.
- Non-closure respected: no plan template, validation script, repo-local skill, or product code was added.
