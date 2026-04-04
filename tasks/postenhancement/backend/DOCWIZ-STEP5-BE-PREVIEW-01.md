# DOCWIZ-STEP5-BE-PREVIEW-01 — Step 5 附件预览后端载体

- Source: `docs/superpowers/plans/2026-04-04-docwiz-step5-preview-implementation.md`
- Type: `backend endpoint/service capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为向导 Step 5 提供 preview-only 附件/模板候选载体，基于当前文书草案投影候选，但不写真实附件。
- Exact closure slice:
  - 新增或扩展 Step 5 attachment preview backend carrier
  - 返回适用 draft rows 的附件/模板候选及可编辑字段
- Explicit non-closure:
  - 不做最终 attachment write integration
  - 不做 dispatch / envelope
  - 不做单文档附件页面增强
- Remaining follow-up task ids:
  - `DOCWIZ-STEP5-FE-PREVIEW-01`
  - `DOCWIZ-QA-STEP5-IMPL-01`
- Allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/tests/test_document_wizard_attachment_preview.py`
  - `docs/superpowers/specs/2026-04-04-docwiz-step5-preview-implementation-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-step5-preview-implementation.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP5-BE-PREVIEW-01.md`
- Verification:
  - `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_attachment_preview.py`
  - `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_attachment_preview.py`
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_attachment_preview.py`
  - `cd backend && pytest -q tests/test_document_wizard_attachment_preview.py`
  - `./scripts/task_validate.sh DOCWIZ-STEP5-BE-PREVIEW-01`

## Execution Checklist

- [ ] Build preview-only attachment candidate response for Step 5
- [ ] Keep preview side-effect-free
- [ ] Cover applicable and empty-state cases with targeted tests
