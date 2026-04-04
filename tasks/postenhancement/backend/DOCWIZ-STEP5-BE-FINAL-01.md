# DOCWIZ-STEP5-BE-FINAL-01 — Step 5 最终提交后端接入

- Source: `docs/superpowers/plans/2026-04-04-docwiz-step5-final-submit-integration.md`
- Type: `backend endpoint/service capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 扩展 wizard final submit backend carrier，接收 Step 5 attachment rows，并在创建真实 `DocAttachment` 时优先使用显式提交值。
- Exact closure slice:
  - 扩展 `/documents/wizard/batch-create` 的 Step 5 final rows schema
  - 校验 Step 5 attachment rows
  - 最终渲染模板并持久化真实附件时消费显式值
- Explicit non-closure:
  - 不做 dispatch / envelope
  - 不做 reporting / status work
  - 不做单文档附件页增强
- Remaining follow-up task ids:
  - `DOCWIZ-STEP5-FE-FINAL-01`
  - `DOCWIZ-QA-STEP5-FINAL-01`
- Allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/tests/test_document_wizard_batch_create.py`
  - `docs/superpowers/specs/2026-04-04-docwiz-step5-final-submit-integration-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-step5-final-submit-integration.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP5-BE-FINAL-01.md`
- Verification:
  - `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_batch_create.py`
  - `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_batch_create.py`
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_batch_create.py`
  - `cd backend && pytest -q tests/test_document_wizard_batch_create.py -k step5`
  - `./scripts/task_validate.sh DOCWIZ-STEP5-BE-FINAL-01`

## Execution Checklist

- [ ] Extend final submit schema with Step 5 attachment rows
- [ ] Validate row and attachment identity
- [ ] Render and persist generated attachments during final submit
