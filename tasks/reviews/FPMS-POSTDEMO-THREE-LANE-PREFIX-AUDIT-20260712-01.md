# FPMS-POSTDEMO-THREE-LANE-PREFIX-AUDIT-20260712-01

## Design References

- `AGENTS.md`
- `docs/postdemo/相关流程操作-20260526.docx`
- `docs/postdemo/OA答复流程.docx`
- `docs/postdemo/信函生成操作.docx`
- `docs/postdemo/专利收费场景-20260626.docx`
- `docs/postdemo/demo-lifecycle-spec2-overlay-v3.html`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md`
- `artifacts/PD-P1-V7-UI-E2E-DEMO-RUN-20260711-01/run-record.md`

## Story Shape Classification

- `shared_file_density`: low; this task file, one new audit report, and task evidence only.
- `prereq_dependency_density`: high; the report reconciles original customer Word documents, V7 design/run evidence, and current code.
- `be_fe_coupling`: read-only high; the findings cover backend state/fee contracts and frontend three-line presentation.
- `evidence_cost`: medium; content, source-path, diff, and task-gate evidence are required.
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Create `docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`, a Chinese pre-fix audit that freezes the customer-source facts for document lists, XML handling, OA/receipt, fee scenarios, and the centered case-lifecycle three-line model; it must identify verified implementation gaps, explicitly distinguish confirmed facts from pending decisions, and prescribe a safe remediation order.

## Explicit Non-Closure

Do not change backend, frontend, database schema, migrations, seed data, tests, V7 demo documents, customer source documents, external-system integration, payment behavior, or any existing review. Do not implement any remediation identified by the audit.

## Allowed Files

- `tasks/reviews/FPMS-POSTDEMO-THREE-LANE-PREFIX-AUDIT-20260712-01.md`
- `docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`
- `artifacts/FPMS-POSTDEMO-THREE-LANE-PREFIX-AUDIT-20260712-01/**`

## Verification Commands

- `rg -n "审计结论|三线模型|文书目录|XML|收费|P0|待确认|实施顺序" docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`
- `git diff --check -- tasks/reviews/FPMS-POSTDEMO-THREE-LANE-PREFIX-AUDIT-20260712-01.md docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`
- `./scripts/task_validate.sh FPMS-POSTDEMO-THREE-LANE-PREFIX-AUDIT-20260712-01`

## Done Definition

- The report separates source facts, verified implementation evidence, proposed design, and pending decisions.
- The report makes the case lifecycle central while preserving document and official-fee overlays.
- The report does not overclaim XML generation, official-system integration, fee coverage, or workflow closure.
- Required evidence exists and the task gate passes.

## Evidence Path

- `artifacts/FPMS-POSTDEMO-THREE-LANE-PREFIX-AUDIT-20260712-01/`

## Remaining Follow-Up Task IDs

None. Every remediation must be planned as a separately approved atomic task.
