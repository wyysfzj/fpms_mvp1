# BADDEBT-FE-BILL-01 — 账单详情页坏账区块。

- Source: `docs/superpowers/plans/2026-03-28-billing-bad-debt-workflow.md`
- Type: `ui component`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 在账单详情页接入新的 billing bad-debt contract，展示坏账主凭证与回收记录，并提供坏账标记、坏账结转、回收坏账入口。
- Covered items:
  - `Priority P1 #6`
- Allowlist:
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/modules/billing/pages/BillDetail.vue`
  - `frontend/src/modules/billing/components/BadDebtPanel.vue`
- Out of scope:
  - `frontend/src/modules/billing/pages/BillList.vue`
  - 独立坏账工作台 / 专门坏账页面
  - 报表页改动
  - `restore / reversal` 交互
  - `frontend/src/api/collections.ts`
- Shared ownership:
  - `Yes`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/modules/billing/pages/BillDetail.vue`
- Verification:
  - `cd frontend && npm run lint -- src/api/billing.ts src/api/billing.types.ts src/modules/billing/pages/BillDetail.vue src/modules/billing/components/BadDebtPanel.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh BADDEBT-FE-BILL-01`

## Exact Closure Slice

- This task closes exactly:
  - 账单详情页使用新的 billing bad-debt read/write contract，展示坏账状态/子状态、坏账主凭证摘要、回收记录列表、累计回收与剩余坏账余额，并提供“标记坏账”“剩余转坏账”“回收坏账”入口；所有用户可见文案必须为简体中文，且不再暴露 restore 交互。

## Explicit Non-Closure Statement

- This task does NOT close:
  - billing/report 列表坏账筛选与汇总
  - 独立坏账页面
  - 坏账冲回 / restore
  - collections 模块的遗留 API 清理

## Remaining Follow-up Task IDs

- `BADDEBT-BE-RPT-01`
- `BADDEBT-FE-RPT-01`
- `BADDEBT-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] bill detail shows bad-debt voucher and recovery list
- [ ] bill detail actions call billing bad-debt APIs only
- [ ] restore UI removed
- [ ] all user-facing text is Simplified Chinese
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/BADDEBT-FE-BILL-01/baseline_allowlist.diff`
- `artifacts/BADDEBT-FE-BILL-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add/update billing API typings and calls only
- [ ] Implement bill-detail bad-debt panel only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
