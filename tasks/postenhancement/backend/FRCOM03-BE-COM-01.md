# FRCOM03-BE-COM-01 — 分摊驱动的提成生成与未冻结重写。

- Source: `docs/superpowers/plans/2026-03-28-fr-com-03-multi-agent-split.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 让 `apply_commission_for_bill()` 在案件配置了 `agent_splits` 时按分摊方案生成多条独立 commission，并在重复应用时仅重写未冻结记录。
- Covered items:
  - `US-COM-03`
  - `FR-COM-03`
- Allowlist:
  - `backend/app/modules/commission/service.py`
  - `backend/tests/test_commission_e2e.py`
- Out of scope:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/billing/service.py`
  - `frontend/src/**`
  - settlement / report 接口改造
  - 新的 commission persistence/schema
  - 已结算或已进入 settlement line 的回溯重写
- Shared ownership:
  - `Yes`
  - `backend/app/modules/commission/service.py`
  - `backend/tests/test_commission_e2e.py`
- Verification:
  - `ruff check backend/app/modules/commission/service.py backend/tests/test_commission_e2e.py`
  - `cd backend && pytest -q tests/test_commission_e2e.py -k 'manual_bill or multi_agent_split'`
  - `./scripts/task_validate.sh FRCOM03-BE-COM-01`

## Exact Closure Slice

- This task closes exactly:
  - `apply_commission_for_bill()` 在案件存在当前有效 `agent_splits` 时，先计算总 commission，再按分摊比例拆成每个代理各自的 commission 记录；再次应用同一账单路径时，只允许重写同一 `case_id/rule_id/fee_type` 下未冻结且未进入 settlement line 的记录，已冻结记录保持不变；未配置分摊时继续走 `primary_agent_id` 单代理 fallback。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 前端案件页分摊编辑
  - settlement / report 输出字段或查询维度变化
  - 专门的“手动重算”API
  - 分摊历史版本化
  - 已结算 / 已入结算行记录的迁移或修复

## Remaining Follow-up Task IDs

- `FRCOM03-FE-CASE-01`
- `FRCOM03-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] multi-agent split creates one commission row per split member
- [ ] repeated apply only rewrites unfrozen records
- [ ] single-agent fallback preserved
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/FRCOM03-BE-COM-01/baseline_allowlist.diff`
- `artifacts/FRCOM03-BE-COM-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing test first
- [ ] Implement the minimum service change only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
