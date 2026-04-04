# DOCWIZ-STEP5-TEMPLATE-SOURCE-01 — Step 5 模板来源 resolver

- Source: `docs/superpowers/plans/2026-04-04-docwiz-step5-template-source-resolution.md`
- Type: `backend service rule`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为 Step 5 后续最终附件生成提供 deterministic 的 `DocTemplate -> Template.file_path` 解析规则。
- Exact closure slice:
  - 更新 `backend/app/modules/documents/service.py`
  - 新增 targeted test 覆盖 resolver 成功/失败语义
- Explicit non-closure:
  - 不做 Step 5 final submit integration
  - 不做 `DocAttachment` 持久化
  - 不做 schema change
- Remaining follow-up task ids:
  - `DOCWIZ-QA-STEP5-TEMPLATE-SOURCE-01`
  - `DOCWIZ-STEP5-ATTACHMENT-PERSIST-01`
  - `DOCWIZ-STEP5-FINAL-SUBMIT-01`
- Allowlist:
  - `backend/app/modules/documents/service.py`
  - `backend/tests/test_document_wizard_template_source_resolution.py`
  - `docs/superpowers/specs/2026-04-04-docwiz-step5-template-source-resolution-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-step5-template-source-resolution.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP5-TEMPLATE-SOURCE-01.md`
- Verification:
  - `ruff check --fix backend/app/modules/documents/service.py backend/tests/test_document_wizard_template_source_resolution.py`
  - `ruff format backend/app/modules/documents/service.py backend/tests/test_document_wizard_template_source_resolution.py`
  - `ruff check backend/app/modules/documents/service.py backend/tests/test_document_wizard_template_source_resolution.py`
  - `cd backend && pytest -q tests/test_document_wizard_template_source_resolution.py`
  - `./scripts/task_validate.sh DOCWIZ-STEP5-TEMPLATE-SOURCE-01`

## Execution Checklist

- [ ] Add deterministic resolver helper
- [ ] Enforce exact-match and conflict semantics
- [ ] Validate resolved file exists
- [ ] Add targeted backend tests
