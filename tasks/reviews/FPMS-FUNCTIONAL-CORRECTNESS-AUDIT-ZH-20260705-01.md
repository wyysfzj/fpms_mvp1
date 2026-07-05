# FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-ZH-20260705-01

## Design References

- `docs/reviews/fpms_functional_correctness_audit_20260705.md`
- `tasks/reviews/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-20260705-01.md`
- `artifacts/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-20260705-01/summary.md`

## Story Shape Classification

- `shared_file_density`: low; only a new Chinese review document and this task file are edited.
- `prereq_dependency_density`: low; the English audit already contains the source-backed findings.
- `be_fe_coupling`: none; this is documentation-only.
- `evidence_cost`: low; structure and whitespace checks are sufficient.
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Create `docs/reviews/fpms_functional_correctness_audit_20260705_zh.md`, a Simplified Chinese version of the existing audit report, preserving the same findings, tables, risk ranking, suggested atomic task breakdown, and Needs Confirmation content.

## Explicit Non-Closure

Do not change product code, backend, frontend, database migrations, tests, E2E fixtures, source customer documents, existing English audit content, or any product behavior.

## Allowed Files

- `tasks/reviews/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-ZH-20260705-01.md`
- `docs/reviews/fpms_functional_correctness_audit_20260705_zh.md`
- `artifacts/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-ZH-20260705-01/**`

## Verification Commands

- `rg -n "总体判断|功能缺失清单|实现正确性问题清单|建议的原子任务拆分" docs/reviews/fpms_functional_correctness_audit_20260705_zh.md`
- whitespace check for `docs/reviews/fpms_functional_correctness_audit_20260705_zh.md` and this task file
- `./scripts/task_validate.sh FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-ZH-20260705-01`

## Done Definition

- Chinese audit document exists.
- It preserves the original report's findings and structure.
- Required sections are present in Simplified Chinese.
- Required evidence artifacts exist under `artifacts/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-ZH-20260705-01/`.
- Task gate passes.

## Evidence Path

- `artifacts/FPMS-FUNCTIONAL-CORRECTNESS-AUDIT-ZH-20260705-01/`

## Remaining Follow-Up Task IDs

None
