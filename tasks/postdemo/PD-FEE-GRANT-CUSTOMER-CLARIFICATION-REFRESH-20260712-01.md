# PD-FEE-GRANT-CUSTOMER-CLARIFICATION-REFRESH-20260712-01

## Design References

- `AGENTS.md`
- `artifacts/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01/analysis/source_ledger.md`
- `docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`
- `docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`

## Story Shape Classification

- `shared_file_density`: low; one existing customer clarification document and task evidence only.
- `prereq_dependency_density`: high; depends on the completed re-audit.
- `be_fe_coupling`: none; customer-facing documentation only.
- `evidence_cost`: medium; questions must be removed or narrowed where new evidence answers them.
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Update `docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md` in plain Simplified Chinese so it incorporates the new customer materials, removes questions now answered by evidence, preserves genuinely unresolved decisions, and clearly separates customer-document facts from system-design choices.

## Explicit Non-Closure

Do not modify customer sources, the audit report, product design, backend, frontend, database, migrations, seed data, tests, or demo behavior. Do not silently choose a remaining customer policy.

## Allowed Files

- `tasks/postdemo/PD-FEE-GRANT-CUSTOMER-CLARIFICATION-REFRESH-20260712-01.md`
- `docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`
- `artifacts/PD-FEE-GRANT-CUSTOMER-CLARIFICATION-REFRESH-20260712-01/**`

## Verification Commands

- `rg -n "客户新增资料|已经明确|仍需确认|标准费率|补充缴费信息模板|相关问题解答|官方文件样例|建议确认结果" docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`
- `git diff --check -- tasks/postdemo/PD-FEE-GRANT-CUSTOMER-CLARIFICATION-REFRESH-20260712-01.md docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`
- `./scripts/task_validate.sh PD-FEE-GRANT-CUSTOMER-CLARIFICATION-REFRESH-20260712-01`

## Evidence Path

- `artifacts/PD-FEE-GRANT-CUSTOMER-CLARIFICATION-REFRESH-20260712-01/`

## Done Definition

- The document remains understandable to non-technical business users.
- New evidence is separated from system-design recommendations.
- Answered questions are converted to confirmed facts.
- Remaining questions are minimal, concrete, and directly decidable.
- Required evidence exists and the task gate passes.

## Remaining Follow-Up Task IDs

`None`. Any product implementation must use separately approved atomic tasks.

