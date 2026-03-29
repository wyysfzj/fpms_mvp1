# PREPAYRPT-FE-01 — 预收款管理报表前端列表页。

- Source: `docs/superpowers/plans/2026-03-29-billing-prepayment-reporting.md`
- Type: `ui page capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 在现有 `PaymentList.vue` 上接入预收款管理报表筛选、列表字段与核心汇总展示，只关闭这个前端 page slice。
- Covered items:
  - `Priority P1 #7`
- Allowlist:
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/modules/billing/pages/PaymentList.vue`
- Out of scope:
  - `frontend/src/modules/billing/pages/PaymentCreate.vue`
  - `frontend/src/modules/billing/pages/BillDetail.vue`
  - 独立预收款报表页面
  - payment / offset 写动作
- Shared ownership:
  - `Yes`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/modules/billing/pages/PaymentList.vue`
- Verification:
  - `cd frontend && npm run lint -- src/api/billing.ts src/api/billing.types.ts src/modules/billing/pages/PaymentList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh PREPAYRPT-FE-01`

## Exact Closure Slice

- This task closes exactly:
  - 现有 `PaymentList.vue` 支持按客户 ID / 预收状态 / 收款日期范围 / 是否仍有剩余预收余额筛选，并展示核心汇总卡片与最小列表字段集：付款编号、客户、收款日期、预收总额、已核销金额、剩余预收余额、预收状态；所有用户可见文案为简体中文。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 独立预收款报表页面
  - 预收款写动作或退款处理
  - 后端 contract 以外的任何模块
  - 复杂分析维度

## Remaining Follow-up Task IDs

- `PREPAYRPT-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] PaymentList 支持预收筛选
- [ ] PaymentList 展示预收汇总
- [ ] 所有用户可见文案为简体中文
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/PREPAYRPT-FE-01/baseline_allowlist.diff`
- `artifacts/PREPAYRPT-FE-01/baseline_external_files.txt`
