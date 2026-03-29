# BADDEBT-BE-ACT-01 — 坏账标记与结转写动作。

- Source: `docs/superpowers/plans/2026-03-28-billing-bad-debt-workflow.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 为 `AR` 账单提供两个正向坏账写动作：手工标记坏账、部分收款后坏账结转；并生成或复用唯一有效坏账主凭证。
- Covered items:
  - `Priority P1 #6`
- Allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
  - `backend/tests/test_billing_bad_debt_actions.py`
- Out of scope:
  - `backend/app/modules/billing/models.py`
  - 回收坏账写动作
  - 坏账冲回 / restore
  - `frontend/src/**`
  - 报表筛选与汇总
- Shared ownership:
  - `Yes`
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/schemas.py`
  - `backend/app/modules/billing/service.py`
- Verification:
  - `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_billing_bad_debt_actions.py`
  - `cd backend && pytest -q tests/test_billing_bad_debt_actions.py -k 'mark or transfer'`
  - `./scripts/task_validate.sh BADDEBT-BE-ACT-01`

## Exact Closure Slice

- This task closes exactly:
  - 为 `AR` 账单新增两个正向坏账动作：手工标记坏账，以及在账单已部分收款时将剩余未收金额结转为坏账；两种路径都必须生成或复用同一条有效坏账主凭证，并正确写入账单坏账状态/子状态。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 回收坏账写入动作
  - 坏账冲回 / restore
  - 独立坏账报表
  - 账单详情前端展示
  - 旧 collections 测试里遗留 bad-debt lifecycle 的全面语义清理

## Remaining Follow-up Task IDs

- `BADDEBT-BE-REC-01`
- `BADDEBT-FE-BILL-01`
- `BADDEBT-BE-RPT-01`
- `BADDEBT-FE-RPT-01`
- `BADDEBT-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] mark bad debt action works for eligible AR bill
- [ ] partial-payment transfer action creates voucher for remaining balance only
- [ ] same bill keeps one effective bad-debt voucher
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/BADDEBT-BE-ACT-01/baseline_allowlist.diff`
- `artifacts/BADDEBT-BE-ACT-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing tests for mark/transfer only
- [ ] Implement minimum write-action contract only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
