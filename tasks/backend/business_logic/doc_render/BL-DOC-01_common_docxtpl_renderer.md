# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Follow design docs in `docs/*.md` and project conventions in `docs/04_backend_architecture.md`
- If a task conflicts with an authoritative design doc, the design doc wins


# BL-DOC-01 — Common docxtpl renderer service (docx bytes)

## Purpose
Implement a reusable server-side `.docx` template renderer using `docxtpl`, as required by MVP1 scope and backend architecture.

Design references:
- `docs/00_mvp1_scope.md` (basic template rendering: docxtpl → docx download)
- `docs/04_backend_architecture.md` (office template rendering)

## Output (EXACTLY ONE FILE)
Create ONE new file:
- `backend/app/common/doc_render/renderer.py`

## Constraints
- No DB schema changes.
- No API endpoint changes in this task.
- One file only.

## Required Interface (Authoritative)
Implement:

```python
class DocxRenderer:
    def render_docx_bytes(self, template_path: str, context: dict) -> bytes:
        ...
```

Rules:
- `template_path` is a filesystem path to a `.docx` template.
- Use `docxtpl.DocxTemplate` to render with the provided context.
- Return rendered `.docx` as bytes in memory (do not write to disk in this function).
- Raise `FileNotFoundError` if template does not exist.
- Raise `ValueError` if template_path does not end with `.docx`.

## Steps
1) Create package folder if missing:
   - `backend/app/common/doc_render/` must be a Python package (`__init__.py` may already exist; if not, do NOT create it in this task—only create `renderer.py` and rely on namespace packages or existing init per repo convention).
2) Implement `DocxRenderer` exactly as interface above.
3) Add minimal internal helper methods only if required, but keep everything inside this single file.
4) Ensure imports are minimal and Ruff-clean.

## Done Criteria
1) File exists at `backend/app/common/doc_render/renderer.py`.
2) A quick import succeeds:
   `PYTHONPATH=backend python -c "from app.common.doc_render.renderer import DocxRenderer; print('OK')"`
