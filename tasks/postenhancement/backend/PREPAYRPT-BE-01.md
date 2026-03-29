# PREPAYRPT-BE-01 — 预收款管理报表后端 list contract。

- Source: `docs/superpowers/plans/2026-03-29-billing-prepayment-reporting.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 扩展 `GET /payments`，支持预收款管理报表筛选与核心汇总字段，只关闭现有 payments list 的后端 contract。
- Covered items:
  - `Priority P1 #7`
- Allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
  - `backend/tests/test_prepayment_reporting_api.py`
- Out of scope:
  - `frontend/src/**`
  - 新的 payment / offset 写动作
  - 独立预收款页面
  - schema / migration 改动
- Shared ownership:
  - `Yes`
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
- Verification:
  - `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_prepayment_reporting_api.py`
  - `cd backend && pytest -q tests/test_prepayment_reporting_api.py`
  - `./scripts/task_validate.sh PREPAYRPT-BE-01`

## Exact Closure Slice

- This task closes exactly:
  - `GET /payments` 支持按 `client_id / prepayment_status / pay_date_from / pay_date_to / has_unapplied_only` 筛选，并返回当前筛选结果集的核心汇总字段：`prepayment_count / prepayment_total_amount / allocated_total_amount / remaining_prepayment_balance`，同时保持现有列表 envelope 不回退。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 前端 PaymentList 页面展示
  - 新的 payment/offset 写动作
  - 独立预收款报表页面
  - 预收款定义重构

## Remaining Follow-up Task IDs

- `PREPAYRPT-FE-01`
- `PREPAYRPT-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] `/payments` 支持预收筛选
- [ ] `/payments` 返回核心汇总字段
- [ ] 现有 list envelope 保持兼容
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PREPAYRPT-BE-01/baseline_allowlist.diff`
- `artifacts/PREPAYRPT-BE-01/baseline_external_files.txt`
