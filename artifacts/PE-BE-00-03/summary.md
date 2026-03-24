# PE-BE-00-03 Evidence Summary

## Task
- ID: PE-BE-00-03
- Runbook: `tasks/postenhancement/backend/PE-BE-00-03.md`

## Scope Compliance
- Changes restricted to allowlisted docs:
  - `docs/error_codes.md`
  - `docs/api_usage_guide.md`
- No runtime code files modified.

## Sections Updated (exact)
- `docs/error_codes.md`
  - `## Error envelope`
  - `## Envelope constraints for post-enhancement domains (mandatory)`
  - `### Post-enhancement domains (reserved conventions)`
  - `#### Annuity`
  - `#### Collections (Dunning / Bad Debt)`
  - `#### Commission`
  - `#### Consulting / Search`
- `docs/api_usage_guide.md`
  - `## Error Response Contract`
  - `## Post-enhancement Domain Status Semantics`
  - `## Common Errors & Fixes` (expanded)

## Consistency Checks Performed
- Markdown fence parity check passed for both files.
- Confirmed current router does not yet include annuity/collections/commission/consulting modules.
- Confirmed current backend behavior:
  - `BusinessError` and `RequestValidationError` use `{"error":{...}}` envelope.
  - Some existing endpoints still use FastAPI `HTTPException` with `{"detail": ...}`.

## Outcome
- Added explicit envelope constraints and domain-specific reserved error/status mappings for annuity, collections, commission, and consulting.
- Kept docs aligned with current backend behavior by documenting both current envelope shapes and route-not-found behavior for not-yet-routed domains.
