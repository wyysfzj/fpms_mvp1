# PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`
- `docs/reviews/fpms_additional_gap_mitigation_close_audit_20260710.md`
- `docs/superpowers/plans/2026-07-10-fpms-additional-gap-mitigation.md`
- `artifacts/PD-POSTDEMO-V8-MITIGATION-DESIGN-20260712-01/summary.md`

## Story Shape Classification

- `shared_file_density`: high; lifecycle, document, fee, migrations, API types, seed, status dictionaries and the case detail page contain shared ownership seams.
- `prereq_dependency_density`: high; projection columns and a shared activity ledger precede every lifecycle, document, fee and overlay integration.
- `be_fe_coupling`: high; the centered three-line UI must consume a frozen backend overlay contract rather than reproduce state logic.
- `evidence_cost`: high; migrations, legal-state transitions, document lineage, fee calculations, workbook fidelity and long-history pagination require direct, per-slice evidence.
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Create one comprehensive V8 implementation plan that translates the approved V8 mitigation design into a dependency-ordered catalog of future atomic task file paths, safe execution waves, exact closure/non-closure contracts, source/test ownership, RED/GREEN commands, independent review and evidence gates. The plan must subtract accepted Tasks 01–70 and be sufficient for a follow-up manifest-materialization task without reopening broad source analysis. Register the plan in `AGENTS.md`.

## Explicit Non-Closure

Do not create the future implementation task files or batch manifest, modify the approved V8 design or historical V6/V7 documents, decide unresolved customer policies, change backend/frontend/database/migrations/seed/tests, run migrations or SQLite-writing tests, execute UI E2E, commit, push, or claim any V8 implementation GAP is closed.

## Allowed Files

- `AGENTS.md`
- `tasks/postdemo/PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `artifacts/PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01.md`
- `rg -n "Story Shape Classification|chosen_runbook|Closed-work subtraction|File ownership map|Dependency DAG|Atomic task catalog|Execution waves|SQLite serialization|Decision gates|RED|GREEN|Evidence|Release close|Non-goals" docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `rg -n "2026-07-12-fpms-postdemo-v8-mitigation-implementation" AGENTS.md`
- `git diff --check -- AGENTS.md tasks/postdemo/PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01.md docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `./scripts/task_validate.sh PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01`

## Evidence Path

- `artifacts/PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01/`

## Done Definition

- The plan starts with the required `writing-plans` header and repeats the approved Story Shape Classification and runbook.
- Accepted Tasks 01–70 are inherited and not silently rescheduled.
- Every future implementation item has one planned exact task file path, one observable closure slice, explicit non-closure, dependencies, likely allowlist ownership, RED/GREEN verification and evidence/gate requirements.
- Shared files and SQLite-writing checks have explicit serialization decisions.
- Customer decision gates are isolated from customer-independent work.
- Wave order provides usable vertical checkpoints without running final-close gates early.
- The follow-up manifest-materialization task can create exact task files without broad design reinterpretation.
- Dirty-baseline artifacts, scoped diff, independent plan review, atomic validation and repository task gate pass.

## Remaining Follow-Up Task IDs

- `PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01`
