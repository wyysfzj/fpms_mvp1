# BADDEBT-FE-RPT-01 — 账单列表坏账筛选与汇总展示。

- Source: `docs/superpowers/plans/2026-03-28-billing-bad-debt-workflow.md`
- Type: `ui page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 在现有账单列表页接入坏账状态筛选与坏账核心汇总展示，消费新的 billing list bad-debt contract，只关闭 bill-list 这一条前端 slice。
- Covered items:
  - `Priority P1 #6`
- Allowlist:
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/modules/billing/pages/BillList.vue`
- Out of scope:
  - `frontend/src/modules/billing/pages/BillDetail.vue`
  - `frontend/src/modules/billing/components/BadDebtPanel.vue`
  - 独立坏账报表页面
  - 其他 billing 页面
  - 坏账写动作或 restore/reversal 交互
- Shared ownership:
  - `Yes`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/modules/billing/pages/BillList.vue`
- Verification:
  - `cd frontend && npm run lint -- src/api/billing.ts src/api/billing.types.ts src/modules/billing/pages/BillList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh BADDEBT-FE-RPT-01`

## Exact Closure Slice

- This task closes exactly:
  - 账单列表页支持按坏账状态筛选，并展示当前结果集的坏账核心汇总字段：坏账账单数、坏账金额、累计回收金额、剩余坏账余额；所有用户可见文案必须为简体中文。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 账单详情坏账区块
  - 独立坏账报表页面
  - 坏账写动作
  - restore / reversal
  - 任何后端 contract 调整

## Remaining Follow-up Task IDs

- `BADDEBT-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] 账单列表支持坏账状态筛选
- [ ] 账单列表展示坏账核心汇总
- [ ] 所有用户可见文案为简体中文
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/BADDEBT-FE-RPT-01/baseline_allowlist.diff`
- `artifacts/BADDEBT-FE-RPT-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add bill-list bad-debt filter and summary display only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
