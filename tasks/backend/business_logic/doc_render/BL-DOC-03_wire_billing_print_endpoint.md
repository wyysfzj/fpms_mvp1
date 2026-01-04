# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Follow design docs in `docs/*.md` and project conventions in `docs/04_backend_architecture.md`
- If a task conflicts with an authoritative design doc, the design doc wins


# BL-DOC-03 — Wire Bill print endpoint to docxtpl renderer (GET /bills/{id}/print)

## Purpose
Implement the MVP1 bill print behavior: server-side docxtpl render → docx download,
by wiring existing Phase 3 endpoint `GET /bills/{id}/print` to:
- `DocxRenderer.render_docx_bytes(...)`
- `BillContextBuilder.build(...)`

Design references:
- `docs/00_mvp1_scope.md`
- `docs/04_backend_architecture.md`
- `docs/permissions_matrix.md` (Bill.Print)

## Output (EXACTLY ONE FILE)
Edit ONLY the existing billing API file that contains the endpoint:
- `backend/app/modules/billing/api.py`

## Preconditions
1) Phase 3 task `BE-APIv4-041_billing_get_bills_id_print.md` is already implemented (endpoint exists).
2) `BL-DOC-01` and `BL-DOC-02` are completed.
3) Template storage convention exists per backend architecture:
   - Dev templates live under `backend/storage/` (or configured storage dir).
4) A Bill template record exists in DB (via Template API) OR a stable configured template path exists in settings/system params.

## Required Behavior (Authoritative)
When calling `GET /bills/<built-in function id>/print`:
1) Enforce permission `Bill.Print` (existing behavior must remain).
2) Load Bill + BillItems + Client (and LetterHead if applicable) from DB.
3) Determine template `.docx` path:
   - Use the existing Bill model/template association if present (preferred), otherwise use a system parameter key:
     - `bill_template_path` in `t_system_param.param_key`
   - This selection rule is fixed:
     - If Bill has explicit template reference -> use it
     - Else -> use system param `bill_template_path`
     - If neither -> return 409 Conflict with detail "Bill template not configured"
4) Build context via `BillContextBuilder.build(...)`.
5) Render docx bytes via `DocxRenderer.render_docx_bytes(template_path, context)`.
6) Return a FastAPI response that downloads a `.docx`:
   - Use `StreamingResponse` or `Response` with:
     - `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
     - `Content-Disposition: attachment; filename="bill_<bill_id>.docx"`

## Error Handling
- If bill not found: 404 (existing behavior)
- If template missing/unconfigured: 409
- If template file missing on disk: 500 with detail "Template file missing"

## Steps
1) Open `backend/app/modules/billing/api.py`.
2) Locate the handler for `GET /bills/{id}/print`.
3) Implement the behavior above using `DocxRenderer` and `BillContextBuilder`.
4) Keep Ruff clean and do not change other endpoints.

## Done Criteria
1) Endpoint returns 200 and downloads a `.docx` when configured.
2) With missing template configuration: returns 409 with exact detail.
3) `ruff check .` passes.
