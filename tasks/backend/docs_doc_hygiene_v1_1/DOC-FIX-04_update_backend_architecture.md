# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Update ONLY the single target file specified by the task
- Align docs with MVP1 scope and current repo structure
- If any statement conflicts with current code or authoritative scope (docs/00_mvp1_scope.md), scope wins


# DOC-FIX-04 — Update docs/04_backend_architecture.md: docxtpl rendering + context builders + Document→Task generation

## Target File (EXACTLY ONE)
- `docs/04_backend_architecture.md`

## Purpose
Ensure architecture doc reflects the implemented Phase 3.5 business logic design.

## Required Edits (Authoritative)
Add/update sections to include:

1) Doc rendering flow (Bill print / Task print):
- API endpoint loads ORM data
- ContextBuilder builds pure dict context
- DocxRenderer renders docx bytes using docxtpl
- Response returns docx download

2) Configuration keys (SystemParam):
- `bill_template_path`
- `task_sheet_template_path`
State that missing config returns 409 from endpoints.

3) Business logic boundaries:
- Rendering + task generation are service-layer concerns
- Phase 3.5 must not change schema

4) Document → Task auto-generation:
- Triggered after document create (OA register path)
- Uses TaskTemplate `offset_days` (or equivalent) to compute due_date
- Idempotency rule to prevent duplicates
- Error behavior: missing template mapping returns 409

## Done Criteria
- The doc clearly describes both doc rendering and auto-task generation flows and config keys.
