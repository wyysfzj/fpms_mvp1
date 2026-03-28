# FRCOM03-DB-01 — 案件级代理人分摊持久化前置任务。

- Source: `docs/superpowers/plans/2026-03-28-fr-com-03-multi-agent-split.md`
- Type: `migration + model`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 新增 `FR-COM-03` 所需的最小案件级代理人分摊持久化结构，并在 ORM 中完成映射。
- Covered items:
  - `US-COM-03`
  - `FR-COM-03`
- Allowlist:
  - `backend/alembic/versions/frcom03_db_01_create_t_case_agent_split.py`
  - `backend/app/modules/cases/models.py`
- Out of scope:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/commission/service.py`
  - `frontend/src/**`
  - 任何结算、报表、权限注册或路由改动
- Shared ownership:
  - `Yes`
  - `backend/app/modules/cases/models.py`
- Verification:
  - `ruff check backend/alembic/versions/frcom03_db_01_create_t_case_agent_split.py backend/app/modules/cases/models.py`
  - `cd backend && python3 -c "import sys; sys.path.insert(0, '.'); from sqlalchemy import inspect; from app.db.session import get_engine; from app.db.base import Base; import app.models  # noqa: F401; engine = get_engine(); tables = set(inspect(engine).get_table_names()); assert 't_case_agent_split' in tables; assert 't_case_agent_split' in Base.metadata.tables"`
  - `cd backend && alembic upgrade heads`
  - `./scripts/task_validate.sh FRCOM03-DB-01`

## Exact Closure Slice

- This task closes exactly:
  - 为案件维护“当前有效代理人分摊方案”新增 SQLite-safe 的持久化表与 `cases` 域 ORM 映射，使后续 case contract 与 commission service 可以在不再扩 schema 的前提下消费该结构。

## Explicit Non-Closure Statement

- This task does NOT close:
  - 案件分摊方案的 API 读写 contract
  - 分摊比例校验与可选代理人权限校验的接口层实现
  - commission 生成或未结算重算逻辑
  - 案件页中的“代理人分摊”前端区块
  - settlement / report 展示或行为变更

## Remaining Follow-up Task IDs

- `FRCOM03-BE-CASE-01`
- `FRCOM03-BE-COM-01`
- `FRCOM03-FE-CASE-01`
- `FRCOM03-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] migration is SQLite-safe
- [ ] ORM imports cleanly
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/FRCOM03-DB-01/baseline_allowlist.diff`
- `artifacts/FRCOM03-DB-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing proof first
- [ ] Implement the minimum persistence only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
