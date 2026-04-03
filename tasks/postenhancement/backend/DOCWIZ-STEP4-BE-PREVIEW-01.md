# DOCWIZ-STEP4-BE-PREVIEW-01 — Step 4 费用预览后端载体

- Source: `docs/superpowers/plans/2026-04-04-docwiz-step4-preview-implementation.md`
- Type: `backend endpoint/service capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为向导 Step 4 提供 preview-only 费用候选载体，基于当前文书草案投影费用草稿候选，但不写真实 `FeeDraft / FeeItem`。
- Exact closure slice:
  - 新增或扩展 Step 4 fee preview backend carrier
  - 返回适用 draft rows 的费用候选及可编辑字段
- Explicit non-closure:
  - 不做最终 fee write integration
  - 不做 Step 5
  - 不做 billing 页面增强
- Remaining follow-up task ids:
  - `DOCWIZ-STEP4-FE-PREVIEW-01`
  - `DOCWIZ-QA-STEP4-IMPL-01`
- Allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_document_wizard_fee_preview.py`
  - `docs/superpowers/specs/2026-04-04-docwiz-step4-preview-implementation-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-step4-preview-implementation.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP4-BE-PREVIEW-01.md`
- Verification:
  - `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_document_wizard_fee_preview.py`
  - `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_document_wizard_fee_preview.py`
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_document_wizard_fee_preview.py`
  - `cd backend && pytest -q tests/test_document_wizard_fee_preview.py`
  - `./scripts/task_validate.sh DOCWIZ-STEP4-BE-PREVIEW-01`

## Execution Checklist

- [ ] Build preview-only fee candidate response for Step 4
- [ ] Keep preview side-effect-free
- [ ] Cover applicable and empty-state cases with targeted tests
