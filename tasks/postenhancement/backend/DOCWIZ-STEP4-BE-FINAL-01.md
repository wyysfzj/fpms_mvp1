# DOCWIZ-STEP4-BE-FINAL-01 — Step 4 最终提交后端接入

- Source: `docs/superpowers/plans/2026-04-04-docwiz-step4-final-submit-integration.md`
- Type: `backend endpoint/service capability`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 扩展 wizard final submit backend carrier，接收 Step 4 fee rows，并在创建真实 `FeeDraft / FeeItem` 时优先使用显式提交值。
- Exact closure slice:
  - 扩展 `/documents/wizard/batch-create` 的 Step 4 final rows schema
  - 校验 Step 4 fee rows
  - 最终创建真实费用草稿与费用项时消费显式值
- Explicit non-closure:
  - 不做 Step 5
  - 不做 billing 页面增强
  - 不做 downstream fee workflow
- Remaining follow-up task ids:
  - `DOCWIZ-STEP4-FE-FINAL-01`
  - `DOCWIZ-QA-STEP4-FINAL-01`
- Allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/tests/test_document_wizard_batch_create.py`
  - `docs/superpowers/specs/2026-04-04-docwiz-step4-final-submit-integration-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-step4-final-submit-integration.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP4-BE-FINAL-01.md`
- Verification:
  - `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_document_wizard_batch_create.py`
  - `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_document_wizard_batch_create.py`
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_document_wizard_batch_create.py`
  - `cd backend && pytest -q tests/test_document_wizard_batch_create.py -k step4`
  - `./scripts/task_validate.sh DOCWIZ-STEP4-BE-FINAL-01`

## Execution Checklist

- [ ] Extend final submit schema with Step 4 fee rows
- [ ] Validate row and fee-item identity
- [ ] Apply explicit fee values before fallback generation
