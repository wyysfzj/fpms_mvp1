# RBSEL-RULE-01 Evidence

Changed only `.worktrees/rbsel-rule-01/AGENTS.md`.

Verification:
- Confirmed the applicability sentence now applies the rule to every multi-step task that will enter `writing-plans` while preserving the approved exclusion for genuinely simple single-file fixes and doc-only tasks.
- Confirmed the timing sentence now requires the spec to record `Story Shape Classification` before entering `writing-plans`.
- Confirmed the plan is still required to record the same classification and `chosen_runbook`.
- `./scripts/task_validate.sh RBSEL-RULE-01` passed.
- Task gate output: `Task Gate PASS`.

No baseline-dirty artifacts were needed.
