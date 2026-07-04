# PD-P1-LIFECYCLE-DEMO-HTML-20260704-01 — 保存第一阶段全流程演示 HTML

## Story Shape Classification

| Dimension | Classification |
| --- | --- |
| shared_file_density | Low. One copied HTML artifact plus this task file and evidence. |
| prereq_dependency_density | Low. Source HTML already exists in the brainstorming companion directory. |
| be_fe_coupling | None. Documentation artifact only. |
| evidence_cost | Low. File existence/content checks and task gate only. |

## chosen_runbook

`P0-single-lane-story`

## Closure

Save the approved `demo-lifecycle-spec2-overlay-v3.html` visual design into `docs/postdemo` beside the Markdown lifecycle demo document, including both the customer-facing dated filename and a same-name copy for traceability back to the brainstorming artifact.

## Non-Closure

Do not modify backend, frontend, database, tests, demo seed data, CPC/OA direct submission, RPA, signature, payment, email behavior, or the existing source companion HTML.

## Allowlist

- `tasks/postdemo/PD-P1-LIFECYCLE-DEMO-HTML-20260704-01.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.html`
- `docs/postdemo/demo-lifecycle-spec2-overlay-v3.html`
- `artifacts/PD-P1-LIFECYCLE-DEMO-HTML-20260704-01/**`

## Inputs

- `.superpowers/brainstorm/75098-1783163908/demo-lifecycle-spec2-overlay-v3.html`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`

## Verification

- Confirm copied HTML exists.
- Confirm copied HTML retains the Chinese lifecycle title and has no English status codes.
- Run `./scripts/task_validate.sh PD-P1-LIFECYCLE-DEMO-HTML-20260704-01`.

## Done Definition

- HTML exists under `docs/postdemo`.
- Same-name copy exists under `docs/postdemo`.
- HTML content matches the approved v3 customer-facing Chinese design.
- Evidence artifacts exist and task gate passes.

## Remaining Follow-Up Task IDs

None.
