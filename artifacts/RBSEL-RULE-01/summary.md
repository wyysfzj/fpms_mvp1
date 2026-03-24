# RBSEL-RULE-01 Evidence

Refreshed `artifacts/RBSEL-RULE-01/**` so they match the RBSEL-RULE-01 product commit `39f432cebd9e84a60487465d115420db5a2f2837` and the scoped baseline-to-commit diff from task baseline `ffd335c`.

Verification:
- Confirmed the applicability trigger is objective: the rule applies whenever there is a written spec, implementation plan, or batch manifest prepared to drive multi-step execution, or when more than one atomic task file or execution wave is required.
- Confirmed the mandatory `Story Shape Classification & Runbook Selection` section is present in full, including the `shared_file_density`, `prereq_dependency_density`, `be_fe_coupling`, `evidence_cost`, and `chosen_runbook` requirements.
- Confirmed both dual-recording requirements are explicit: `Story Shape Classification` must appear in spec and resulting plan, and `chosen_runbook` must appear in both spec and plan.
- Confirmed the valid `chosen_runbook` IDs are explicitly enumerated as `P0-single-lane-story`, `P0-prereq-heavy-story`, `P0-multi-lane-parallel-story`, and `P0-frontend-heavy-story`.
- Confirmed the replanning language is present and enforceable: new shared prerequisite, shared ownership conflict, and state-machine reachability issues all force a return to planning, and follow-up work must be split when the closure slice changes.
- Confirmed the scoped diff evidence was regenerated from baseline commit `ffd335c` to immutable product commit `39f432cebd9e84a60487465d115420db5a2f2837`.
- `./scripts/task_validate.sh RBSEL-RULE-01` passed.
- Task gate output: `Task Gate PASS`.

Scoped diff evidence was regenerated from task baseline `ffd335c` to immutable product commit `39f432cebd9e84a60487465d115420db5a2f2837` in `artifacts/RBSEL-RULE-01/git/diff.patch`.

No baseline-dirty artifacts were needed.
