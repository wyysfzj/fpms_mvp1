# BADDEBT-BE-BILL-01 — 账单详情坏账链路只读 contract。

- Source: `docs/superpowers/plans/2026-03-28-billing-bad-debt-workflow.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 扩展 `GET /bills/{bill_id}`，返回坏账状态/子状态、坏账主凭证摘要和回收记录列表，只关闭账单详情坏账链路的只读 contract。
- Covered items:
  - `Priority P1 #6`
- Allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
  - `backend/tests/test_billing_bad_debt_detail_api.py`
- Out of scope:
  - `backend/app/modules/billing/models.py`
  - 任何坏账写动作 endpoint
  - `frontend/src/**`
  - 报表筛选与汇总
  - 坏账冲回
- Shared ownership:
  - `Yes`
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
- Verification:
  - `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_billing_bad_debt_detail_api.py`
  - `cd backend && pytest -q tests/test_billing_bad_debt_detail_api.py`
  - `./scripts/task_validate.sh BADDEBT-BE-BILL-01`

## Exact Closure Slice

- This task closes exactly:
  - `GET /bills/{bill_id}` 在保持现有账单详情字段不回退的前提下，新增只读坏账链路字段：账单坏账状态/子状态、坏账主凭证摘要、回收记录列表、累计回收金额与剩余坏账余额。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 标记坏账或坏账结转动作
  - 回收坏账写入动作
  - 坏账报表筛选与汇总
  - 前端账单详情页展示
  - 旧坏账 lifecycle endpoint 的语义调整

## Remaining Follow-up Task IDs

- `BADDEDT-BE-ACT-01`
- `BADDEBT-BE-REC-01`
- `BADDEBT-FE-BILL-01`
- `BADDEBT-BE-RPT-01`
- `BADDEBT-FE-RPT-01`
- `BADDEBT-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] `GET /bills/{bill_id}` 返回坏账摘要与回收记录
- [ ] 账单详情原有字段保持兼容
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/BADDEBT-BE-BILL-01/baseline_allowlist.diff`
- `artifacts/BADDEBT-BE-BILL-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add/adjust read-only schemas and endpoint mapping only
- [ ] Add targeted regression test
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
