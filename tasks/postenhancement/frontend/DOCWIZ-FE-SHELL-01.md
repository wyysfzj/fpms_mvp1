# DOCWIZ-FE-SHELL-01 — 中间文件向导页面壳与 stepper。

- Source: `docs/superpowers/plans/2026-03-29-documents-step12-wizard.md`
- Type: `ui shell`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 新增向导页面壳、stepper 与前端内存状态容器，只关闭 UI shell slice。
- Covered items:
  - `Priority P1 #8`
- Allowlist:
  - `frontend/src/router/index.ts`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
- Out of scope:
  - Step 1 案件解析细节
  - Step 2 逐案编辑细节
  - 任何 backend 代码
- Shared ownership:
  - `Yes`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
- Verification:
  - `cd frontend && npm run lint -- src/router/index.ts src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentWizard.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-FE-SHELL-01`

## Exact Closure Slice

- This task closes exactly:
  - 一个新的中间文件向导页面壳，包含两步 stepper、共享状态容器、前后步导航与空白占位，不包含具体 Step1/Step2 业务细节。

## Explicit Non-Closure Statement

- This task does NOT close:
  - Step 1 逐行案件解析
  - Step 2 行编辑与批量提交
  - 任何 backend contract

## Remaining Follow-up Task IDs

- `DOCWIZ-FE-STEP1-01`
- `DOCWIZ-FE-STEP2-01`
- `DOCWIZ-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] wizard route added
- [ ] stepper shell added
- [ ] in-memory state container added
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/DOCWIZ-FE-SHELL-01/baseline_allowlist.diff`
- `artifacts/DOCWIZ-FE-SHELL-01/baseline_external_files.txt`
