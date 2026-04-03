# DOCWIZ-STEP3-BE-PREVIEW-01 — Step 3 任务候选预览后端承载

- Source: `docs/superpowers/plans/2026-04-03-docwiz-step3-preview-implementation.md`
- Type: `backend endpoint capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为向导 Step 3 提供 preview-only 的任务候选投影能力，不写入真实 `T_Task`。
- Exact closure slice:
  - 更新 `backend/app/modules/documents/api.py`
  - 更新 `backend/app/modules/documents/service.py`
  - 更新 `backend/app/modules/documents/schemas.py`
- Explicit non-closure:
  - 不做最终提交 integration
  - 不做 Step 4/5
  - 不做 schema 变更
- Remaining follow-up task ids:
  - `DOCWIZ-STEP3-FE-PREVIEW-01`
  - `DOCWIZ-QA-STEP3-IMPL-01`
- Allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/tests/test_document_wizard_task_preview.py`
  - `docs/superpowers/specs/2026-04-03-docwiz-step3-preview-implementation-design.md`
  - `docs/superpowers/plans/2026-04-03-docwiz-step3-preview-implementation.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP3-BE-PREVIEW-01.md`
- Verification:
  - `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py`
  - `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py`
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_task_preview.py`
  - `cd backend && pytest -q tests/test_document_wizard_task_preview.py`
  - `./scripts/task_validate.sh DOCWIZ-STEP3-BE-PREVIEW-01`

## Execution Checklist

- [ ] Add preview-only request/response schema
- [ ] Add preview-only service projection
- [ ] Add documents module preview endpoint with parameter-injected permission
- [ ] Keep preview side-effect-free
