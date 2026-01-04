# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Follow design docs in `docs/*.md` and project conventions in `docs/04_backend_architecture.md`
- If a task conflicts with an authoritative design doc, the design doc wins


# BL-TASK-02 — Wire Document register endpoint to TaskGenerationService (OA → auto tasks)

## Purpose
After a document is created via the existing Phase 3 document register endpoint,
trigger TaskGenerationService to auto-create tasks (minimal OA behavior) and persist them.

Design references:
- `docs/00_mvp1_scope.md`
- `docs/03_database_mvp1_subset.md` (Document → Case; Task → Case; TaskTemplate)
- `docs/04_backend_architecture.md`

## Output (EXACTLY ONE FILE)
Edit ONLY the documents API file that implements document create:
- `backend/app/modules/documents/api.py`

## Preconditions
1) Phase 3 endpoint for creating documents exists (task `BE-APIv4-012_documents_post_documents.md`).
2) `BL-TASK-01` is completed.

## Required Behavior (Authoritative)
In the handler that creates a new Document:
1) After successfully committing the new Document, call:
   - `TaskGenerationService().generate_from_document(db, document)`
2) If tasks are created, commit them and their logs in the same request.
3) Response behavior:
   - Do NOT change the existing response shape (Phase 3 contract must remain).
   - If the response currently returns the created document only, keep that.
   - Add a response header:
     - `X-Auto-Tasks-Created: <N>`
     where N is number of tasks created (0 allowed).
4) Error handling:
   - If generation fails due to missing TaskTemplate mapping (RuntimeError), return 409 with detail.
   - Do not partially commit; rollback on exception.

## Done Criteria
1) Creating a document that matches templates results in tasks created (verify via GET /tasks).
2) Response includes header `X-Auto-Tasks-Created`.
3) Existing document create response body contract remains unchanged.
