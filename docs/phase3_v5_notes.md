# Phase 3 API Tasks — v5 completeness notes

This package is generated as "v4 unified" and includes:
- Unified permission codes (Title.Action) aligned to docs/02_permissions_rbac.md naming style
- Request/Response examples derived from migrations (minimum required fields)
- Curl smoke examples

If you want a "v5" more complete version, the next increment would add:
1) Schema-driven request/response examples:
   - Generate Pydantic schemas first, then derive examples from schema (preferred).
2) Per-endpoint error codes:
   - 400/401/403/404/409 mappings based on business rules docs.
3) Permission mapping strictness:
   - Replace heuristic resource mapping with an explicit RBAC table and seed data.
4) Endpoint-specific payload samples:
   - For /bills/from-drafts, provide realistic draft_ids array payload.
