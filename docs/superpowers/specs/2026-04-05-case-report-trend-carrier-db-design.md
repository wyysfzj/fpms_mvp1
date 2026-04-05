# CASERPT-TREND-CARRIER-DB-01 Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `backend schema prerequisite only`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`#13 所有统计报表` 当前只剩 `RPT-CASE` 的 `year/month trend reporting` 无法诚实闭合。原因不是前端缺卡片，也不是 service 没聚合，而是 `Case` 缺少 terminal-event date carrier。若没有这些持久字段，就无法对以下趋势给出真实时间轴：

- `TERMINATED`
- `INVALIDATED`
- `WITHDRAWN`
- `ABANDONED`

## Scope

- 为 `Case` 新增 4 个 terminal-event date carrier
- 提供 SQLite-safe Alembic prerequisite migration
- 提供 ORM/schema-level regression test，证明字段和 SQLite 列真实存在

## Explicit Non-scope

- 不实现 `CASERPT-TREND-01`
- 不实现任何趋势 API/UI
- 不做 review close update
- 不吸收其他 case report residual

## Carrier Decision

本轮采用最小持久化 carrier strategy：

- `Case.terminated_date`
- `Case.invalidated_date`
- `Case.withdrawn_date`
- `Case.abandoned_date`

不引入 event ledger，不改现有统计接口，不做状态推导重构。

## Affected Files

- `backend/app/modules/cases/models.py`
- `backend/alembic/versions/<new migration>.py`
- `backend/tests/test_case_trend_carrier_schema.py`

## Verification

- task-scoped Ruff format/check
- targeted SQLite schema test
- task gate for implementation task
- task gate for QA task

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
