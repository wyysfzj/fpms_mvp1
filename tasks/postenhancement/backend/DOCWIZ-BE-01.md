# DOCWIZ-BE-01 — 中间文件向导 Step1-2 批量创建后端 contract。

- Source: `docs/superpowers/plans/2026-03-29-documents-step12-wizard.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 新增中间文件向导的批量创建 API 与服务编排，只关闭 Step1-2 批量创建 contract。
- Covered items:
  - `Priority P1 #8`
- Allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/app/modules/documents/service.py`
  - `backend/tests/test_document_wizard_batch_create.py`
- Out of scope:
  - `frontend/src/**`
  - Step 3/4/5 UI
  - schema / migration 改动
  - 单条 `/documents` contract 重构
- Shared ownership:
  - `Yes`
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/app/modules/documents/service.py`
- Verification:
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_document_wizard_batch_create.py`
  - `cd backend && pytest -q tests/test_document_wizard_batch_create.py`
  - `./scripts/task_validate.sh DOCWIZ-BE-01`

## Exact Closure Slice

- This task closes exactly:
  - 一个向导专用批量创建 endpoint，接收 Step1 批次共享字段与 Step2 行级最小字段集，统一校验并一次性批量创建多条 `T_Document`。

## Explicit Non-Closure Statement

- This task does NOT close:
  - Step 1 前端案件解析 UI
  - Step 2 前端逐案编辑 UI
  - Step 3/4/5 的任务、费用、附件 UI
  - schema 改动

## Remaining Follow-up Task IDs

- `DOCWIZ-FE-SHELL-01`
- `DOCWIZ-FE-STEP1-01`
- `DOCWIZ-FE-STEP2-01`
- `DOCWIZ-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] batch create endpoint added
- [ ] row-level validation and error contract implemented
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/DOCWIZ-BE-01/baseline_allowlist.diff`
- `artifacts/DOCWIZ-BE-01/baseline_external_files.txt`
