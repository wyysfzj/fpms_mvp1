# FRCOM03-BE-CASE-01 — 案件分摊方案 contract 读写前置任务。

- Source: `docs/superpowers/plans/2026-03-28-fr-com-03-multi-agent-split.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 为案件详情与案件更新 contract 增加“当前有效代理人分摊方案”的读写能力与最小校验。
- Covered items:
  - `US-COM-03`
  - `FR-COM-03`
- Allowlist:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
  - `backend/tests/test_case_agent_split_api.py`
- Out of scope:
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/commission/api.py`
  - `frontend/src/**`
  - 结算、报表、分摊重算
  - 新增权限码或路由 wiring
- Shared ownership:
  - `Yes`
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/service.py`
- Verification:
  - `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_agent_split_api.py`
  - `cd backend && pytest -q tests/test_case_agent_split_api.py`
  - `./scripts/task_validate.sh FRCOM03-BE-CASE-01`

## Exact Closure Slice

- This task closes exactly:
  - `GET /cases/{id}` 返回案件当前有效代理人分摊方案，且 `PUT /cases/{id}` 能保存该方案并完成最小业务校验，包括成员唯一、比例和为 `100%`、仅允许内部代理相关用户、未配置时允许为空。

## Explicit Non-Closure Statement

- This task does NOT close:
  - commission 按分摊方案生成或未结算重算
  - 冻结记录判定
  - 前端案件页“代理人分摊”编辑区块
  - settlement / report 的任何行为变化
  - 分摊历史版本化

## Remaining Follow-up Task IDs

- `FRCOM03-BE-COM-01`
- `FRCOM03-FE-CASE-01`
- `FRCOM03-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] case detail returns split config
- [ ] case update persists validated split config
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/FRCOM03-BE-CASE-01/baseline_allowlist.diff`
- `artifacts/FRCOM03-BE-CASE-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing API proof first
- [ ] Implement the minimum contract and validation only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
