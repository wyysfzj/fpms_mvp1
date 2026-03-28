# FRCOM03-FE-CASE-01 — 案件页代理人分摊编辑区块。

- Source: `docs/superpowers/plans/2026-03-28-fr-com-03-multi-agent-split.md`
- Type: `page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal:
  - 在案件编辑页内提供“代理人分摊”中文编辑区块，并对接现有 case contract 的 `agent_splits`。
- Covered items:
  - `US-COM-03`
  - `FR-COM-03`
- Allowlist:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/modules/cases/components/CaseAgentSplitEditor.vue`
- Out of scope:
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `frontend/src/modules/commission/**`
  - settlement / report 页面
  - 多版本分摊历史展示
  - 新的全局 store / router 变更
- Shared ownership:
  - `Yes`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
- Verification:
  - `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseEdit.vue src/modules/cases/components/CaseAgentSplitEditor.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh FRCOM03-FE-CASE-01`

## Exact Closure Slice

- This task closes exactly:
  - `CaseEdit` 页面可以加载、编辑并提交 `agent_splits`，用户能维护多行“代理人 / 角色 / 分摊比例”，表单使用简体中文提示，并在前端做最小校验：成员不可重复、比例必须为正、总和必须等于 `100`、允许清空为 `[]`。

## Explicit Non-Closure Statement

- This task does NOT close:
  - `CaseDetail` 展示优化
  - commission 列表/结算/报表页面联动
  - 用户搜索器或远程用户选择弹窗重做
  - 分摊历史版本化
  - 多页联动或 dashboard 展示

## Remaining Follow-up Task IDs

- `FRCOM03-QA-01`

## Done Definition

- [ ] exact closure slice implemented
- [ ] no out-of-scope expansion
- [ ] CaseEdit round-trips `agent_splits`
- [ ] visible UI text is Simplified Chinese
- [ ] verification passed
- [ ] artifacts generated
- [ ] task gate passed

## Dirty Baseline Artifacts

- `artifacts/FRCOM03-FE-CASE-01/baseline_allowlist.diff`
- `artifacts/FRCOM03-FE-CASE-01/baseline_external_files.txt`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Record baseline artifacts before editing
- [ ] Add failing UI proof first
- [ ] Implement the minimum edit UI only
- [ ] Run required verification
- [ ] Generate evidence artifacts
- [ ] Run task gate
- [ ] Stop after one closure slice
