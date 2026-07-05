# PD-DOC-ATTACHMENT-UPLOAD-ONE-STEP-UX-20260705-01 — 附件上传单弹窗交互

## Story Shape Classification

- shared_file_density: Low. This task owns one document upload component and one focused frontend smoke test.
- prereq_dependency_density: Low. Existing `uploadAttachment(docId, file, metadata)` API already supports role metadata.
- be_fe_coupling: Low. No backend contract change is expected.
- evidence_cost: Medium. Requires a RED/GREEN source smoke, frontend typecheck, browser verification, and task gate.
- chosen_runbook: `P0-frontend-heavy-story`

## Exact Closure Slice

将附件上传前端交互改为单弹窗单确认流程：点击“上传附件”后，在同一弹窗内选择文件、附件角色、历史别名，并点击“确认上传”后一次性提交。

## Explicit Non-Closure

不修改后端数据模型，不新增官方自动上传，不修改 60 项官文目录，不改变附件存储规则，不实现批量上传，不修改后端 API。

## Allowed Files

- `tasks/postdemo/PD-DOC-ATTACHMENT-UPLOAD-ONE-STEP-UX-20260705-01.md`
- `frontend/src/modules/documents/components/AttachmentList.vue`
- `frontend/tests/attachment-upload-one-step-source.mjs`
- `artifacts/PD-DOC-ATTACHMENT-UPLOAD-ONE-STEP-UX-20260705-01/**`

## Verification Commands

- `cd frontend && node tests/attachment-upload-one-step-source.mjs`
- `cd frontend && npm run typecheck`
- Browser/in-app UI verification against a local frontend build or dev server when available.
- `./scripts/task_validate.sh PD-DOC-ATTACHMENT-UPLOAD-ONE-STEP-UX-20260705-01`

## Evidence Path

- `artifacts/PD-DOC-ATTACHMENT-UPLOAD-ONE-STEP-UX-20260705-01/`

## Done Definition

- 页面常驻区域只有一个“上传附件”入口，不再常驻显示角色/历史别名下拉。
- 点击入口后出现标题为“上传附件”的弹窗。
- 弹窗内包含“选择文件”“附件角色”“历史别名（可选）”“确认上传”“取消”。
- 选择文件只暂存本次上传 draft，不会立即调用 `uploadAttachment`。
- 点击“确认上传”后才调用现有 `uploadAttachment`。
- 未选择文件点击确认时提示“请先选择文件”。
- 上传成功提示“附件上传成功”，并清空 draft、关闭弹窗、刷新附件列表。

## Remaining Follow-Up Task IDs

None.
