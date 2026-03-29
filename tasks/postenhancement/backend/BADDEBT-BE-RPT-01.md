# BADDEBT-BE-RPT-01 — 账单列表坏账筛选与汇总 contract。

- Source: `docs/superpowers/plans/2026-03-28-billing-bad-debt-workflow.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 扩展 `GET /bills`，支持坏账状态筛选，并返回当前列表结果集对应的坏账核心汇总口径，只关闭列表/报表后端 contract 这一条 slice。
- Covered items:
  - `Priority P1 #6`
- Allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
  - `backend/tests/test_billing_bad_debt_reporting.py`
- Out of scope:
  - `backend/app/modules/billing/models.py`
  - `GET /bills/{bill_id}`
  - 任何坏账写动作 endpoint
  - `frontend/src/**`
  - 独立坏账报表页面
  - 坏账冲回
- Shared ownership:
  - `Yes`
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
- Verification:
  - `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_billing_bad_debt_reporting.py`
  - `cd backend && pytest -q tests/test_billing_bad_debt_reporting.py`
  - `./scripts/task_validate.sh BADDEBT-BE-RPT-01`

## Exact Closure Slice

- This task closes exactly:
  - `GET /bills` 支持按坏账状态筛选，并在保持现有分页列表 envelope 不回退的前提下，返回当前结果集的坏账核心汇总字段：坏账账单数、坏账金额、累计回收金额、剩余坏账余额。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 账单详情坏账链路展示
  - 标记坏账、坏账结转、回收坏账写动作
  - 前端账单列表筛选控件与汇总展示
  - 独立坏账报表页面
  - 坏账冲回或历史补录

## Remaining Follow-up Task IDs

- `BADDEBT-FE-RPT-01`
- `BADDEBT-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] `GET /bills` 支持坏账状态筛选
- [ ] `GET /bills` 返回坏账核心汇总口径
- [ ] 原有分页列表字段保持兼容
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/BADDEBT-BE-RPT-01/baseline_allowlist.diff`
- `artifacts/BADDEBT-BE-RPT-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add bill-list bad-debt filter and summary contract only
- [ ] Add targeted regression test
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
