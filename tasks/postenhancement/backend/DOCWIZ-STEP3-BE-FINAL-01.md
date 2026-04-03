# DOCWIZ-STEP3-BE-FINAL-01 — Step 3 最终提交后端接入

- Source: `docs/superpowers/plans/2026-04-03-docwiz-step3-final-submit-integration.md`
- Type: `backend service rule`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 扩展 wizard final submit carrier 接收 Step 3 任务行，并在创建真实任务时优先使用显式提交值。
- Exact closure slice:
  - 更新 `backend/app/modules/documents/api.py`
  - 更新 `backend/app/modules/documents/service.py`
  - 更新 `backend/app/modules/documents/schemas.py`
  - 更新 `backend/tests/test_document_wizard_batch_create.py`
- Explicit non-closure:
  - 不做 Step 4/5
  - 不做 assignment semantics
  - 不做 schema 变更
- Remaining follow-up task ids:
  - `DOCWIZ-STEP3-FE-FINAL-01`
  - `DOCWIZ-QA-STEP3-FINAL-01`
- Allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/tests/test_document_wizard_batch_create.py`
  - `docs/superpowers/specs/2026-04-03-docwiz-step3-final-submit-integration-design.md`
  - `docs/superpowers/plans/2026-04-03-docwiz-step3-final-submit-integration.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP3-BE-FINAL-01.md`
- Verification:
  - `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_batch_create.py`
  - `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_batch_create.py`
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_batch_create.py`
  - `cd backend && pytest -q tests/test_document_wizard_batch_create.py`
  - `./scripts/task_validate.sh DOCWIZ-STEP3-BE-FINAL-01`

## Execution Checklist

- [ ] Extend final submit schema with Step 3 task rows
- [ ] Validate Step 3 task row identity and shape
- [ ] Create real tasks from explicit values first
- [ ] Keep untouched fields falling back to default generation
