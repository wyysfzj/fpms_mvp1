# PD-ENH-P1-DEV-PLAN-20260531-01 — P1 full-scope development planning

## Exact Closure Slice

Create the planning-only implementation plan, batch manifest, and atomic follow-up task files needed to develop the full P1 scope from `docs/postdemo/postdemo_p1_functional_spec_20260531.md`.

## Explicit Non-Closure

No backend product code, frontend product code, database migration, CPC/OA direct-submit implementation, RPA, email sending, or execution of the generated follow-up implementation tasks.

## Remaining Follow-Up Task IDs

Defined by `tasks/postdemo/PD-ENH-P1-DEV-MANIFEST-20260531-01.md`.

None of these follow-up tasks may be absorbed into this planning task.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | High. P1 touches shared case, document, attachment, fee, template, frontend API, route/menu, and migration surfaces. |
| prereq_dependency_density | High. Case official fields, attachment manifest roles, work-package carriers, and status semantics must exist before UI and full-flow QA. |
| be_fe_coupling | High. Frontend pages depend on backend schema/API contracts for official fields, work packages, file roles, receipt metadata, fee checklist, and letter handoff. |
| evidence_cost | High. Each backend task needs scoped Ruff and targeted pytest; each frontend task needs lint/type/build and browser evidence; final QA needs item-to-slice ledger. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postdemo/PD-ENH-P1-DEV-PLAN-20260531-01.md`
- `tasks/postdemo/PD-ENH-P1-DEV-MANIFEST-20260531-01.md`
- `tasks/postdemo/PD-P1-*.md`
- `docs/superpowers/plans/2026-05-31-postdemo-p1-full-scope-development.md`
- `artifacts/PD-ENH-P1-DEV-PLAN-20260531-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-ENH-P1-DEV-PLAN-20260531-01.md`
- `python3 - <<'PY' ... PY` planning consistency check
- `./scripts/task_validate.sh PD-ENH-P1-DEV-PLAN-20260531-01`

## Evidence Path

- `artifacts/PD-ENH-P1-DEV-PLAN-20260531-01/`
