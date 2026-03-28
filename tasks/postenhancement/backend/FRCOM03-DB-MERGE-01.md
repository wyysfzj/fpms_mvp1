# FRCOM03-DB-MERGE-01 — 修复 FR-COM-03 的 Alembic 双 head blocker。

- Source: `docs/superpowers/plans/2026-03-28-fr-com-03-alembic-single-head-prereq.md`
- Type: `db prerequisite`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 新增一个 Alembic merge revision，把当前两个 migration head 合并为单 head，解除 `FRCOM03-BE-COM-01` 的 pytest 前置阻塞。
- Covered items:
  - `US-COM-03`
  - `FR-COM-03`
- Allowlist:
  - `backend/alembic/versions/*.py`
- Out of scope:
  - `backend/app/modules/commission/service.py`
  - `backend/tests/test_commission_e2e.py`
  - `backend/tests/conftest.py`
  - 修改任何既有 migration 的业务 DDL
  - 任何 frontend / API / service 行为改动
- Shared ownership:
  - `Yes`
  - `backend/alembic/versions/*.py`
- Verification:
  - `cd backend && alembic heads`
  - `cd backend && alembic upgrade head`
  - `./scripts/task_validate.sh FRCOM03-DB-MERGE-01`

## Exact Closure Slice

- This task closes exactly:
  - 通过新增一个空的 merge migration，把当前 Alembic graph 的两个 head 合并成单一 head，使仓库重新满足 `upgrade(..., "head")` 的既有测试夹具假设。

## Explicit Non-Closure Statement

- This task does NOT close:
  - `FRCOM03-BE-COM-01` 的 commission 逻辑实现或复审
  - pytest 断言内容本身
  - 任意业务表结构 redesign

## Remaining Follow-up Task IDs

- `FRCOM03-BE-COM-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] repo Alembic graph reduced to one head
- [ ] `alembic upgrade head` succeeds
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record current head state before editing
- [ ] Add merge revision only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Stop after one closure slice
