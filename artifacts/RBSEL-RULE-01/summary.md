# RBSEL-RULE-01 Evidence Summary

- Task: add the mandatory `AGENTS.md` rule section for story-shape classification and runbook selection.
- Modified file: `AGENTS.md`
- Verification: `rg -n "Story Shape Classification|chosen_runbook|Replan|planning" AGENTS.md`
- Result: pass
- Closure slice: add the mandatory repo rule section requiring story-shape classification, `chosen_runbook`, and replanning on new shared prerequisites.
- Non-closure respected: no skill file, template, gate script, or product code was created.
