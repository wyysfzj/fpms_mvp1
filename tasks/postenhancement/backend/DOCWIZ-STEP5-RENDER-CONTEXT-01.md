# DOCWIZ-STEP5-RENDER-CONTEXT-01 — Step 5 渲染上下文 helper

- Source: `docs/superpowers/plans/2026-04-04-docwiz-step5-render-context.md`
- Type: `backend service rule`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为 Step 5 后续最终模板生成提供 documents-side render context helper。
- Exact closure slice:
  - 更新 `backend/app/modules/documents/service.py`
  - 新增 targeted test 覆盖 context 字段集
- Explicit non-closure:
  - 不做 Step 5 final submit integration
  - 不调用模板渲染
  - 不做 API/schema change
- Remaining follow-up task ids:
  - `DOCWIZ-QA-STEP5-RENDER-CONTEXT-01`
  - `DOCWIZ-STEP5-FINAL-SUBMIT-01`
- Allowlist:
  - `backend/app/modules/documents/service.py`
  - `backend/tests/test_document_template_render_context.py`
  - `docs/superpowers/specs/2026-04-04-docwiz-step5-render-context-design.md`
  - `docs/superpowers/plans/2026-04-04-docwiz-step5-render-context.md`
  - `tasks/postenhancement/backend/DOCWIZ-STEP5-RENDER-CONTEXT-01.md`
- Verification:
  - `ruff check --fix backend/app/modules/documents/service.py backend/tests/test_document_template_render_context.py`
  - `ruff format backend/app/modules/documents/service.py backend/tests/test_document_template_render_context.py`
  - `ruff check backend/app/modules/documents/service.py backend/tests/test_document_template_render_context.py`
  - `cd backend && pytest -q tests/test_document_template_render_context.py`
  - `./scripts/task_validate.sh DOCWIZ-STEP5-RENDER-CONTEXT-01`

## Execution Checklist

- [ ] Add render-context helper
- [ ] Expose stable document/case/client field set
- [ ] Keep helper side-effect-free
- [ ] Add targeted backend tests
