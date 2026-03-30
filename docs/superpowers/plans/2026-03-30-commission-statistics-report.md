# Commission Statistics Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成 `RPT-COM` 第一轮最小闭环：在现有 commission 模块中提供稳定的提成金额统计报表。

**Architecture:** 继续复用现有 settlement report endpoint 与 `CommissionSettlement.vue`，按 `backend report contract`、`frontend reporting slice`、`QA close` 三个原子任务推进，避免新建页面或引入新的报表平台壳。

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3, Element Plus, existing commission APIs

---

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `chained (BE -> FE)`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

### Task 1: `COMRPT-BE-01`

- `task file path`: `tasks/postenhancement/backend/COMRPT-BE-01.md`
- `closure slice`:
  - 收敛并补齐 commission settlement report backend contract，使其稳定提供第一轮报表闭环所需的筛选、summary、按代理人统计、按案件统计、明细列表
- `explicit non-closure`:
  - 不做 schema 变更
  - 不做成本占比分析
  - 不做图表/打印/导出
  - 不改前端页面
- `allowlist`:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
  - `backend/tests/test_commission_report.py`
- `verification`:
  - `python3 -m ruff check backend/app/modules/commission/api.py backend/app/modules/commission/service.py backend/tests/test_commission_report.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_commission_report.py`
  - `./scripts/task_validate.sh COMRPT-BE-01`
- `evidence path`:
  - `artifacts/COMRPT-BE-01/**`
- `dependency notes`:
  - frontend 依赖此 contract 收敛结果

### Task 2: `COMRPT-FE-01`

- `task file path`: `tasks/postenhancement/frontend/COMRPT-FE-01.md`
- `closure slice`:
  - 在现有 `CommissionSettlement.vue` 上收敛报表展示，使第一轮最小闭环完整可用：筛选、summary cards、按代理人统计、按案件统计、明细列表
- `explicit non-closure`:
  - 不新建独立 `CommissionReport.vue`
  - 不改批次创建/明细生成逻辑
  - 不做图表/打印/导出
  - 不做成本占比分析
- `allowlist`:
  - `frontend/src/api/commission.ts`
  - `frontend/src/api/commission.types.ts`
  - `frontend/src/modules/commission/pages/CommissionSettlement.vue`
- `verification`:
  - `cd frontend && npm run lint -- src/api/commission.ts src/api/commission.types.ts src/modules/commission/pages/CommissionSettlement.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh COMRPT-FE-01`
- `evidence path`:
  - `artifacts/COMRPT-FE-01/**`
- `dependency notes`:
  - 串行依赖 `COMRPT-BE-01`

### Task 3: `COMRPT-QA-01`

- `task file path`: `tasks/postenhancement/backend/COMRPT-QA-01.md`
- `closure slice`:
  - 对 `RPT-COM` 故事做 item-to-slice ledger、evidence audit、故事级收口
- `explicit non-closure`:
  - 不改任何产品代码
- `allowlist`:
  - `artifacts/COMRPT-QA-01/**`
- `verification`:
  - `./scripts/task_validate.sh COMRPT-BE-01`
  - `./scripts/task_validate.sh COMRPT-FE-01`
  - `./scripts/task_validate.sh COMRPT-QA-01`
- `evidence path`:
  - `artifacts/COMRPT-QA-01/**`
- `dependency notes`:
  - 串行依赖前两个任务完成

## Wave Order

- Wave 1: `COMRPT-BE-01`
- Wave 2: `COMRPT-FE-01`
- Wave 3: `COMRPT-QA-01`

## Serialized Ownership Decisions

- `backend/app/modules/commission/api.py`
  - only `COMRPT-BE-01`
- `backend/app/modules/commission/service.py`
  - only `COMRPT-BE-01`
- `frontend/src/api/commission.ts`
  - only `COMRPT-FE-01`
- `frontend/src/api/commission.types.ts`
  - only `COMRPT-FE-01`
- `frontend/src/modules/commission/pages/CommissionSettlement.vue`
  - only `COMRPT-FE-01`

## Done Definition

`RPT-COM` 可被标记完成，当且仅当：

- `COMRPT-BE-01`、`COMRPT-FE-01`、`COMRPT-QA-01` 全部 `PASS`
- backend report contract 稳定覆盖：
  - `totals`
  - `by_agent`
  - `by_case`
  - `details`
- frontend 页面完整展示第一轮最小闭环
- 所有 evidence 目录齐全
- 所有 task gate 通过
