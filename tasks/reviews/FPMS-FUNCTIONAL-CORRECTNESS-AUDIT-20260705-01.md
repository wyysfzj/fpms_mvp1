# FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-20260705-01

## Design References

- `AGENTS.md`
- `docs/TXX.pdf`
- `docs/FPMS SPEC 2.0.md`
- `docs/postdemo/相关流程操作-20260526.docx`
- `docs/postdemo/OA答复流程.docx`
- `docs/postdemo/信函生成操作.docx`
- `docs/postdemo/专利收费场景-20260626.docx`
- `/Users/cfcc/Documents/相关问题解答.docx`
- `docs/postdemo/postdemo_enhancement_analysis_20260530.md`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `docs/postdemo/postdemo_p1_e2e_demo_20260612.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`
- `docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`
- `artifacts/PD-ENH-*/summary.md`
- `artifacts/PD-P1-*/summary.md`
- `artifacts/PD-FEE-SCENARIO-*/summary.md`
- `artifacts/PD-DOC-*/summary.md`

## Story Shape Classification

- `shared_file_density`: low; only one review document and this task file are edited.
- `prereq_dependency_density`: medium; source documents, implementation evidence, and current code must be cross-checked before writing findings.
- `be_fe_coupling`: read-only high; the audit spans backend, frontend, tests, and E2E, but does not edit product files.
- `evidence_cost`: medium; static scans and targeted source/evidence checks are required.
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Generate `docs/reviews/fpms_functional_correctness_audit_20260705.md`, an evidence-backed FPMS functional completeness and implementation correctness audit with overall judgment, functional gap table, correctness issue table, ranked high-risk summary, follow-up atomic task breakdown, and Needs Confirmation section.

## Explicit Non-Closure

Do not modify backend, frontend, database migrations, seed data, tests, E2E fixtures, customer source documents, product behavior, UI behavior, RPA/CPC/OA direct-submit behavior, or existing design specs. Do not fix any issue found by the audit.

## Allowed Files

- `tasks/reviews/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-20260705-01.md`
- `docs/reviews/fpms_functional_correctness_audit_20260705.md`
- `artifacts/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-20260705-01/**`

## Verification Commands

- `rg -n "Overall Judgment|Functional Gap List|Implementation Correctness Issues|Suggested Atomic Task Breakdown" docs/reviews/fpms_functional_correctness_audit_20260705.md`
- `git diff --check -- docs/reviews/fpms_functional_correctness_audit_20260705.md tasks/reviews/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-20260705-01.md`
- `./scripts/task_validate.sh FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-20260705-01`

## Done Definition

- The audit document exists and contains the required sections and tables.
- Findings cite source documents, implementation files, tests, or evidence summaries.
- Unknowns are marked `Needs confirmation`.
- Required evidence artifacts exist under `artifacts/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-20260705-01/`.
- Task gate passes.

## Evidence Path

- `artifacts/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-20260705-01/`

## Remaining Follow-Up Task IDs

None
