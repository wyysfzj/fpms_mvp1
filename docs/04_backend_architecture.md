# Backend Architecture (FastAPI)

## Structure principles
- Modular by domain (`app/modules/*`)
- Within each module:
  - `models.py` (SQLAlchemy models)
  - `schemas.py` (Pydantic DTOs)
  - `service.py` (business logic)
  - `api.py` (FastAPI router)
  - `docs/` (this is the contract for Copilot/Codex to follow)

## Cross-cutting modules
- `core/` — settings, logging, security helpers
- `db/` — session management, base model
- `common/` — shared primitives (pagination, errors, enums, file storage)

## Error model
Return consistent error response:
```json
{
  "error": {
    "code": "CASE_NO_DUPLICATE",
    "message": "CaseNo must be unique",
    "details": {"case_no":"CN-2025-0001"}
  }
}
```
- Always map business validation to stable error codes.

## Auth
- JWT access token for MVP1
- RBAC enforced per endpoint

## File storage (attachments/templates)
- Dev: local folder `backend/storage/`
- Prod: docker volume mounted to `/app/storage`
- Future: S3/OSS adapter (see module future docs)

## Office template rendering
- docxtpl renders `.docx` with Jinja2 variables
- Maintain template context builders per output type (bill, task sheet, document cover)
- For MVP1, output `.docx` only; PDF conversion is future.

