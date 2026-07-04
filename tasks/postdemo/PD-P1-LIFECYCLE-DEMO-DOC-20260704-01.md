# PD-P1-LIFECYCLE-DEMO-DOC-20260704-01 — 第一阶段专利案件全流程演示设计文档

## Story Shape Classification

| Dimension | Classification |
| --- | --- |
| shared_file_density | Low. One new post-demo document plus this task file and evidence artifacts. |
| prereq_dependency_density | Low. Inputs are existing specs and the approved v3 visual design. |
| be_fe_coupling | None. Documentation-only task. |
| evidence_cost | Low. Markdown content checks and task gate only. |

## chosen_runbook

`P0-single-lane-story`

## Closure

Create a new Chinese demo design document that captures the approved v3 lifecycle demo structure: one patent case from new filing through examination, OA reply, grant, grant fee, annuity task, and annuity pay-list, with Chinese legal-status wording and customer-facing demo steps.

## Non-Closure

Do not modify backend, frontend, database, E2E tests, demo seed data, browser companion HTML, CPC/OA direct submission, RPA, signature, automatic payment, or email sending behavior.

## Allowlist

- `tasks/postdemo/PD-P1-LIFECYCLE-DEMO-DOC-20260704-01.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `artifacts/PD-P1-LIFECYCLE-DEMO-DOC-20260704-01/**`

## Inputs

- `docs/FPMS SPEC 2.0.md`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `.superpowers/brainstorm/75098-1783163908/demo-lifecycle-spec2-overlay-v3.html`

## Verification

- `python3 - <<'PY' ...` content check for required Chinese legal statuses and no English status codes in the new demo document.
- `./scripts/task_validate.sh PD-P1-LIFECYCLE-DEMO-DOC-20260704-01`

## Done Definition

- New document exists under `docs/postdemo`.
- Demo status wording is Chinese and customer-facing.
- Document includes source basis, status mainline, demo runbook, fee/annuity coverage, and scope boundary.
- Evidence artifacts exist and task gate passes.

## Remaining Follow-Up Task IDs

None.
