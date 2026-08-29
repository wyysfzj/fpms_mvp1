# FPMS-DEMO-V6-POSTDEMO-INDEX-CLEANUP-20260829-03

## Objective

Give colleagues one current `docs/postdemo` entry point and remove seven superseded operational demo artifacts that are not consumed by active code or tests.

## Exact Closure Slice

- Add `docs/postdemo/README.md` as the unique current V6 demo index.
- Point colleagues to the quickstart, canonical handoff, runbook, lifecycle page, and seed data.
- State that historical specs/tasks remain audit records and are not current execution instructions.
- List the seven retired paths and the exact Git commit from which they remain recoverable.
- Delete only those seven retired files.

## Explicit Non-Closure

- Do not delete V5 lifecycle files because active compatibility tests still consume them.
- Do not rewrite historical specs, plans, tasks, reviews, source registries, or authority records.
- Do not change product code, tests, release state, tags, receipts, business facts, or V6 contracts.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-V6-FINAL-CANDIDATE-CLOSE-20260829-04`

## Allowed Files

- `docs/postdemo/README.md`
- `docs/postdemo/postdemo_p1_v4_ui_e2e_success_runbook_20260705.md`
- `docs/postdemo/postdemo_p1_v5_ui_e2e_success_runbook_20260705.md`
- `docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md`
- `docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_v7_20260711.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.html`
- `tasks/postdemo/FPMS-DEMO-V6-POSTDEMO-INDEX-CLEANUP-20260829-03.md`

## Verification Commands

- The seven retired paths do not exist.
- The five current colleague-facing V6 documents exist and are linked by the index.
- `docs/postdemo/demo-lifecycle-customer-v5.html` and its runbook still exist.
- No non-document/task source file refers to any retired path.
- `git diff --check` passes and scope is limited to this allowlist.

## Evidence Path

- `artifacts/FPMS-DEMO-V6-POSTDEMO-INDEX-CLEANUP-20260829-03/`
