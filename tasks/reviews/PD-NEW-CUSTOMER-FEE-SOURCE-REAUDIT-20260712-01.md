# PD-NEW-CUSTOMER-FEE-SOURCE-REAUDIT-20260712-01

## Design References

- `AGENTS.md`
- `artifacts/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01/analysis/source_ledger.md`
- `docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`
- `docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`

## Story Shape Classification

- `shared_file_density`: low; one existing audit report and task evidence only.
- `prereq_dependency_density`: high; depends on the completed source-index task and source ledger.
- `be_fe_coupling`: read-only high; implementation consequences span fee, document, and case-state behavior.
- `evidence_cost`: high; each changed conclusion must map new customer evidence to current design/implementation.
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Update `docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md` with a dated re-review addendum that evaluates the new standard-rate workbook, supplemental-payment template, customer answers, sample/template library, official fee page, and Tianyue fee page; revise only conclusions that the new evidence confirms, narrows, contradicts, or leaves unresolved.

## Explicit Non-Closure

Do not modify customer sources, the clarification document, product design, backend, frontend, database, migrations, seed data, tests, or demo behavior. Do not implement any finding.

## Allowed Files

- `tasks/reviews/PD-NEW-CUSTOMER-FEE-SOURCE-REAUDIT-20260712-01.md`
- `docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`
- `artifacts/PD-NEW-CUSTOMER-FEE-SOURCE-REAUDIT-20260712-01/**`

## Verification Commands

- `rg -n "新增客户资料复审|标准费率|补充缴费信息模板|相关问题解答|文件样例及模版|集成电路布图设计|天悦知识产权|结论变化" docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`
- `git diff --check -- tasks/reviews/PD-NEW-CUSTOMER-FEE-SOURCE-REAUDIT-20260712-01.md docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`
- `./scripts/task_validate.sh PD-NEW-CUSTOMER-FEE-SOURCE-REAUDIT-20260712-01`

## Evidence Path

- `artifacts/PD-NEW-CUSTOMER-FEE-SOURCE-REAUDIT-20260712-01/`

## Done Definition

- New source facts and source authority are explicit.
- Prior findings are marked confirmed, narrowed, superseded, or still pending.
- Rate, payment-template, document-template, and grant-evidence impacts are addressed.
- Required evidence exists and the task gate passes.

## Remaining Follow-Up Task IDs

- `PD-FEE-GRANT-CUSTOMER-CLARIFICATION-REFRESH-20260712-01`

