# RBSEL-RULE-01 Evidence

Updated `.worktrees/rbsel-rule-01/AGENTS.md` and refreshed `artifacts/RBSEL-RULE-01/**`.

Verification:
- Confirmed the mandatory `Story Shape Classification & Runbook Selection` section is present in full, including the `shared_file_density`, `prereq_dependency_density`, `be_fe_coupling`, `evidence_cost`, and `chosen_runbook` requirements.
- Confirmed the valid `chosen_runbook` IDs are explicitly enumerated as `P0-single-lane-story`, `P0-prereq-heavy-story`, `P0-multi-lane-parallel-story`, and `P0-frontend-heavy-story`.
- Confirmed the replanning language is present and enforceable: new shared prerequisite, shared ownership conflict, and state-machine reachability issues all force a return to planning, and follow-up work must be split when the closure slice changes.
- Confirmed the applicability sentence now uses a process-based exclusion for single-file fix and doc-only tasks handled outside `writing-plans`, without subjective wording.
- Confirmed the permission snippet code fence is now closed and the Markdown renders correctly.
- `./scripts/task_validate.sh RBSEL-RULE-01` passed.
- Task gate output: `Task Gate PASS`.

Scoped diff evidence was regenerated from task baseline `0e78d0` to `HEAD` in `artifacts/RBSEL-RULE-01/git/diff.patch`.

No baseline-dirty artifacts were needed.
