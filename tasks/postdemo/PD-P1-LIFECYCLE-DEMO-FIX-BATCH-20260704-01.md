# PD-P1-LIFECYCLE-DEMO-FIX-BATCH-20260704-01

## Batch Goal

Close the P1 lifecycle demo blockers found in `artifacts/PD-P1-LIFECYCLE-DEMO-UI-WALKTHROUGH-20260704-01/summary.md`, then rerun the visible UI demo until the script can show a coherent case lifecycle in Simplified Chinese.

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high

## chosen_runbook

`P0-prereq-heavy-story`

## Batch Closure

Coordinate the atomic tasks below. Each task has exactly one closure slice and independent evidence. The batch is complete only when all implementation tasks pass and the final visible demo rerun passes.

## Batch Non-Closure

Do not implement CPC/OA direct submit, RPA, scan-code signature automation, automatic official payment, or Longxia email sending.

## Atomic Tasks

| Order | Task file | Closure slice | Non-closure |
| --- | --- | --- | --- |
| 1 | `tasks/postdemo/PD-P1-GRANT-NOTICE-UPLOAD-LIFECYCLE-20260704-01.md` | Grant notice attachment upload with ready grant fields advances the case to `GRANTED`, creates/reuses a grant-fee task, and updates the demo fixture/script to use that file-driven path. | No frontend route redesign, no automatic official submit, no annuity UI changes. |
| 2 | `tasks/postdemo/PD-P1-CASE-EDIT-GRANT-FIELDS-I18N-20260704-01.md` | Case edit page clearly displays and saves grant, annuity-monitoring, and customer fee-reduction fields using Simplified Chinese business labels. | No backend schema changes, no new case lifecycle transitions. |
| 3 | `tasks/postdemo/PD-P1-WORKFLOW-DEMO-I18N-RECEIPT-20260704-01.md` | P1 official workflow/document/fee demo pages do not expose internal status codes and show recorded OA receipt metadata back to the user. | No backend receipt model changes unless a display-only API mapping bug is proven. |
| 4 | `tasks/postdemo/PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01.md` | Reseed demo data and rerun the full visible UI script, announcing each step and expected result before UI input, until the demo passes or a new atomic blocker is filed. | No product code fixes inside the rerun task except evidence-only updates. |

## Serialized Shared Files

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py` is touched only in task 1.
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md` is touched only in task 1 unless a later task discovers a script wording bug.
- Frontend P1 display files are serialized through tasks 2 and 3.

## Done Definition

- Every task has `artifacts/<TASK-ID>/results.jsonl`, `summary.md`, `git/diff.patch`, and dirty baseline artifacts when required.
- Every task runs `./scripts/task_validate.sh <TASK-ID>`.
- Final rerun produces screenshots/observations and no P1 in-scope blocker remains.
