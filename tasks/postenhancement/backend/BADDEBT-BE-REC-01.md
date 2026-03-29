# BADDEBT-BE-REC-01 — 回收坏账写动作。

- Source: `docs/superpowers/plans/2026-03-28-billing-bad-debt-workflow.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 为坏账主凭证新增回收坏账写动作，支持多次部分回收，并保证累计回收不超过坏账主凭证金额。
- Covered items:
  - `Priority P1 #6`
- Allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
  - `backend/tests/test_billing_bad_debt_recovery.py`
- Out of scope:
  - `backend/app/modules/billing/models.py`
  - 坏账冲回 / restore
  - 坏账报表筛选与汇总
  - `frontend/src/**`
  - 旧 collections bad-debt lifecycle 清理
- Shared ownership:
  - `Yes`
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
- Verification:
  - `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_billing_bad_debt_recovery.py`
  - `cd backend && pytest -q tests/test_billing_bad_debt_recovery.py`
  - `./scripts/task_validate.sh BADDEBT-BE-REC-01`

## Exact Closure Slice

- This task closes exactly:
  - 为已存在坏账主凭证的 `AR` 账单新增回收坏账写动作，允许多次部分回收；每次回收必须新增独立回收记录，更新主凭证累计回收金额与剩余坏账余额，并禁止累计回收超过坏账主凭证金额。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 坏账冲回 / restore
  - 标记坏账或坏账结转动作
  - 独立坏账报表
  - 账单详情前端展示
  - 历史坏账补录

## Remaining Follow-up Task IDs

- `BADDEBT-FE-BILL-01`
- `BADDEBT-BE-RPT-01`
- `BADDEBT-FE-RPT-01`
- `BADDEBT-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] recovery action creates one recovery record per call
- [ ] multiple partial recoveries supported
- [ ] total recovered amount cannot exceed voucher amount
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/BADDEBT-BE-REC-01/baseline_allowlist.diff`
- `artifacts/BADDEBT-BE-REC-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing tests for recovery only
- [ ] Implement minimum recovery contract only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
