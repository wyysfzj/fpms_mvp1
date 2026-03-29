# DOCWIZ-FE-STEP2-01 — 中间文件向导 Step 2 逐案编辑与提交。

- Source: `docs/superpowers/plans/2026-03-29-documents-step12-wizard.md`
- Type: `ui step capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 实现 Step 2 收窄字段集编辑与批量提交，只关闭 Step 2 slice。
- Covered items:
  - `Priority P1 #8`
- Allowlist:
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
- Out of scope:
  - Step 3/4/5 UI
  - 草稿持久化
  - 复杂动态字段渲染器
  - `NeedNotifyAgent` 独立持久化
- Shared ownership:
  - `Yes`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/modules/documents/pages/DocumentWizard.vue`
- Verification:
  - `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentWizard.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DOCWIZ-FE-STEP2-01`

## Exact Closure Slice

- This task closes exactly:
  - Step 2 支持逐案编辑当前 contract 可承载字段：`title / doc_date / ref_no / need_reply / reply_to_id / extra_data`，调用批量创建 endpoint，并显示成功或失败反馈。

## Explicit Non-Closure Statement

- This task does NOT close:
  - Step 3/4/5
  - 复杂动态字段引擎
  - 附件上传或模板渲染
  - `NeedNotifyAgent / Summary / Remark` 的独立结构化承载

## Remaining Follow-up Task IDs

- `DOCWIZ-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] row editing UI added
- [ ] batch submit wired
- [ ] `extra_data` 文本补充区支持
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/DOCWIZ-FE-STEP2-01/baseline_allowlist.diff`
- `artifacts/DOCWIZ-FE-STEP2-01/baseline_external_files.txt`
