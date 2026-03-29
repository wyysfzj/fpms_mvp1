# DOCWIZ-FE-STEP1-01 — 中间文件向导 Step 1 案件解析。

- Source: `docs/superpowers/plans/2026-03-29-documents-step12-wizard.md`
- Type: `ui step capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 实现 Step 1 的逐行案件输入、解析结果和错误回显，只关闭 Step 1 slice。
- Covered items:
  - `Priority P1 #8`
- Allowlist:
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
- Out of scope:
  - Step 2 行编辑
  - backend 合同扩展
  - 案件查询结果导入
- Shared ownership:
  - `Yes`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
- Verification:
  - `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentWizard.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-FE-STEP1-01`

## Exact Closure Slice

- This task closes exactly:
  - Step 1 支持逐行输入案卷号/申请号、展示成功案件列表与失败行错误，并在至少有 1 条有效案件时允许进入 Step 2。

## Explicit Non-Closure Statement

- This task does NOT close:
  - Step 2 字段编辑或提交
  - 从案件查询结果导入
  - 草稿持久化

## Remaining Follow-up Task IDs

- `DOCWIZ-FE-STEP2-01`
- `DOCWIZ-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] multiline parse UI added
- [ ] row-level errors rendered
- [ ] Step 2 gate enforced
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/DOCWIZ-FE-STEP1-01/baseline_allowlist.diff`
- `artifacts/DOCWIZ-FE-STEP1-01/baseline_external_files.txt`
