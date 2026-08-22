# PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Team Lead / documentation materializer

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- `tasks/postdemo/PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01.md`
- `artifacts/PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01/analysis/tasks01_70_inheritance_index.md`
- `artifacts/PD-POSTDEMO-V8-MITIGATION-IMPLEMENTATION-PLAN-20260712-01/analysis/independent_review.md`

## Story Shape Classification

- `shared_file_density`: high; this task materializes every future shared-file ownership declaration and the only foundation manifest.
- `prereq_dependency_density`: high; 283 catalog rows include migrations, shared seams, customer gates and final-close dependencies.
- `be_fe_coupling`: high; backend/frontend task contracts must preserve the approved overlay and adapter ordering without implementation.
- `evidence_cost`: high; every task shape, dependency, gate classification, inherited evidence link and manifest count requires mechanical validation.
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Mechanically materialize the independently approved V8 plan into exactly 283 atomic task files under `tasks/postdemo/v8/`, one frozen 197-task foundation manifest, and machine-readable catalog, dependency, gate, Tasks01–70 inheritance, item-to-slice and shared-file/SQLite serialization indexes under this task's artifact directory. Copy the approved task profiles, exact observable closure, explicit non-closure, allowlist, RED/GREEN verification, evidence/gate requirements and canonical dependencies without reopening business-source analysis or implementing any catalog task.

## Explicit Non-Closure

Do not implement, execute or approve any of the 283 catalog tasks; do not create a gate-lane or full-program manifest; do not modify product code, migrations, seed, implementation tests, approved design/plan, V6/V7 history or customer source files; do not decide unresolved customer policies; do not run SQLite-writing tests, repo-wide Ruff/pytest/frontend build/Playwright/release gate; do not commit, push, reset, clean, stash, checkout or discard user changes.

## Allowed Files

- `tasks/postdemo/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01.md`
- `tasks/postdemo/v8/**`
- `tasks/batches/FPMS-POSTDEMO-V8-FOUNDATION-20260712-01.md`
- `artifacts/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. The approved design, plan and inherited evidence are read-only inputs.

## Materialization Contract

- Catalog cardinality is exactly `283 = 197 foundation + 86 customer-dependent/full-only`.
- Every catalog path appears once in the plan, once in the machine-readable catalog and once as a real task file.
- Every generated task declares exactly one `Task Contract Profile`, one exact closure slice, one explicit non-closure, canonical dependencies, exact allowlist, RED/GREEN commands, evidence path, task gate, and `Remaining Follow-Up Task IDs: None`.
- The foundation manifest contains exactly the 197 foundation rows and excludes all 86 deferred rows with their exact gate/full-only classification preserved in the gate register.
- The manifest contains no duplicate task path, no undeclared path and no customer-dependent/full-only path.
- Tasks01–70 remain inherited regression/evidence inputs and are not regenerated or rescheduled.
- The 15-row P0/P1 ledger expands plan section references to exact catalog task IDs without marking any implementation item covered.
- Canonical dependencies resolve to existing catalog IDs or an explicitly named external/inherited prerequisite; dependency closure has no self-cycle.
- Shared ownership and all SQLite-writing verification remain serialized exactly as frozen in the approved plan.

## Verification Commands

- Task shape: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01.md`
- RED/GREEN materialization contract: `python3 artifacts/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01/analysis/validate_materialization.py`
- Generated task shapes: run `evidence_gate.py check-task` for every sorted `tasks/postdemo/v8/*.md` path.
- Scope/format: `git diff --check -- tasks/postdemo/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01.md tasks/postdemo/v8 tasks/batches/FPMS-POSTDEMO-V8-FOUNDATION-20260712-01.md`
- Evidence: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`
- Repository task gate: `./scripts/task_validate.sh PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01`

## Evidence Path

- `artifacts/PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01/**`

## Done Definition

- The task file passes atomic shape validation.
- RED evidence proves required outputs were absent before generation.
- All 283 task files, the 197-task foundation manifest and every required machine-readable index exist and pass the materialization validator.
- Every generated task independently passes task-shape validation.
- Dirty baseline, baseline-subtracted scoped diff, independent read-only review, atomic evidence validation and repository task gate pass.
- Exact closure is complete and explicit non-closure is respected.

## Remaining Follow-Up Task IDs

- `FPMS-V8-MANIFEST-RELEASE-GATE-20260712-01`
- `FPMS-V8-CATALOG-MANIFEST-COVERAGE-GATE-20260712-01`
