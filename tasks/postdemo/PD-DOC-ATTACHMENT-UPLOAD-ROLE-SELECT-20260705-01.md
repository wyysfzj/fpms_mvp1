# PD-DOC-ATTACHMENT-UPLOAD-ROLE-SELECT-20260705-01 — 附件上传角色/历史别名选择

## Story Shape Classification

- shared_file_density: Medium. Touches upload API, frontend API client, and one upload component.
- prereq_dependency_density: Low. `DocAttachment` already has metadata columns and service-level validation.
- be_fe_coupling: High. Backend multipart contract and frontend form must align.
- evidence_cost: Medium. Requires backend API tests, frontend typecheck, and task gate.
- chosen_runbook: `P0-frontend-heavy-story`

## Closure

上传附件时支持选择 `official_file_role` 和 `source_role_alias`；后端 multipart API 保存并返回这些字段；前端附件上传区域提供简体中文下拉，至少覆盖现有附件角色和客户旧系统历史别名，上传后附件列表显示选择结果。

## Non-Closure

不新增官方提交自动上传，不把 60 项官文清单全部塞入附件角色，不改变已有附件存储路径规则，不新增数据库表或 migration。

## Allowlist

- `tasks/postdemo/PD-DOC-ATTACHMENT-UPLOAD-ROLE-SELECT-20260705-01.md`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_document_attachment_upload_metadata_api.py`
- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/components/AttachmentList.vue`
- `artifacts/PD-DOC-ATTACHMENT-UPLOAD-ROLE-SELECT-20260705-01/**`

## Verification

- `cd backend && ruff check --fix app/modules/documents/api.py tests/test_document_attachment_upload_metadata_api.py`
- `cd backend && ruff format app/modules/documents/api.py tests/test_document_attachment_upload_metadata_api.py`
- `cd backend && ruff check app/modules/documents/api.py tests/test_document_attachment_upload_metadata_api.py`
- `cd backend && pytest tests/test_document_attachment_upload_metadata_api.py -q`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh PD-DOC-ATTACHMENT-UPLOAD-ROLE-SELECT-20260705-01`

## Done Definition

- Multipart upload accepts `official_file_role` and `source_role_alias`.
- Invalid `official_file_role` returns business error instead of being silently saved.
- Response and subsequent document detail include role, alias, upload position, package usage hint, hash, and evidence flags.
- Frontend upload UI can choose these Simplified Chinese options: 技术交底书, 委托指示, XML压缩包, 合并PDF, OA意见陈述 Word, OA意见陈述 PDF, 修改后的权利要求书, 修改对照页, 其他证明文件, 电子申请回执, PCT 公开文本, 补正后说明书, 递交电子申请文件, 客户提供原始文件.

## Follow-Up Task IDs

None.

