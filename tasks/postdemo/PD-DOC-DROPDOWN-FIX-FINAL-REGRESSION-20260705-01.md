# PD-DOC-DROPDOWN-FIX-FINAL-REGRESSION-20260705-01 — 下拉修复最终回归收口

## Story Shape Classification

- shared_file_density: Low. Audit/evidence only.
- prereq_dependency_density: Medium. Depends on Task A and Task B passing.
- be_fe_coupling: Medium. Confirms backend and frontend contract together.
- evidence_cost: Medium. Runs targeted regression plus task gates.
- chosen_runbook: `P0-prereq-heavy-story`

## Closure

对本 batch 做最终收口审计，映射客户反馈到 Task A/Task B evidence，运行必要 backend targeted regression 和 frontend typecheck/build，并确认未把官文目录混入附件角色枚举。

## Non-Closure

不新增产品功能，不修复新发现的独立 bug，不做 CPC/OA direct submit、RPA、自动签名或自动上传官方系统。

## Allowlist

- `tasks/postdemo/PD-DOC-DROPDOWN-FIX-FINAL-REGRESSION-20260705-01.md`
- `artifacts/PD-DOC-DROPDOWN-FIX-FINAL-REGRESSION-20260705-01/**`

## Verification

- `cd backend && pytest tests/test_official_notice_catalog_seed.py tests/test_document_attachment_upload_metadata_api.py -q`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- `./scripts/task_validate.sh PD-DOC-DROPDOWN-FIX-FINAL-REGRESSION-20260705-01`

## Done Definition

- Final summary includes a customer-feedback-to-task ledger.
- Official notice catalog coverage and attachment upload role coverage are both evidence-backed.
- Explicit residual non-scope is recorded.

## Follow-Up Task IDs

None.

