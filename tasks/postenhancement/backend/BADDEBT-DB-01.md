# BADDEBT-DB-01 — 坏账主凭证与回收记录持久化前置。

- Source: `docs/superpowers/plans/2026-03-28-billing-bad-debt-workflow.md`
- Type: `db prerequisite`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 为 `AR` 账单坏账流程新增坏账主凭证与回收记录持久化结构，并为账单提供坏账状态/子状态承载。
- Covered items:
  - `Priority P1 #6`
- Allowlist:
  - `backend/alembic/versions/baddebt_db_01_create_bad_debt_tables.py`
  - `backend/app/modules/billing/models.py`
- Out of scope:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/service.py`
  - `frontend/src/**`
  - 报表筛选与汇总
  - 坏账动作实现
- Shared ownership:
  - `Yes`
  - `backend/app/modules/billing/models.py`
  - `backend/alembic/versions/baddebt_db_01_create_bad_debt_tables.py`
- Verification:
  - `ruff check backend/alembic/versions/baddebt_db_01_create_bad_debt_tables.py backend/app/modules/billing/models.py`
  - `cd backend && alembic upgrade head`
  - `./scripts/task_validate.sh BADDEBT-DB-01`

## Exact Closure Slice

- This task closes exactly:
  - 为 `AR` 账单坏账流程新增一个坏账主凭证表、一个坏账回收记录表，并在账单模型上新增坏账状态/子状态承载字段，使后续 bill-detail action、recovery、report 切片可以消费稳定持久化结构。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 标记坏账或坏账结转动作
  - 回收坏账动作
  - 账单详情页 UI
  - billing/report 列表筛选与汇总

## Remaining Follow-up Task IDs

- `BADDEBT-BE-BILL-01`
- `BADDEBT-BE-ACT-01`
- `BADDEBT-BE-REC-01`
- `BADDEBT-FE-BILL-01`
- `BADDEBT-BE-RPT-01`
- `BADDEBT-FE-RPT-01`
- `BADDEBT-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] bad-debt master voucher persistence exists
- [ ] recovery persistence exists
- [ ] AR bill bad-debt state carriers exist
- [ ] SQLite-safe migration verified
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/BADDEBT-DB-01/baseline_allowlist.diff`
- `artifacts/BADDEBT-DB-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add migration/model changes only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
