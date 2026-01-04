# Integration Tasks

## INT-01 OpenAPI export + TS type generation (optional MVP1)
- Backend: export openapi json to `docs/openapi.json`
- Frontend: use `openapi-typescript` to generate TS types

## INT-02 E2E smoke test
- Use Playwright (future) or minimal manual checklist:
  1. Login
  2. Create Client
  3. Create Case
  4. Register Document + Attachment
  5. Create Task and see in Today view
  6. Create Fee Draft -> Generate Bill
  7. Register Payment -> Offset -> Bill becomes SETTLED
  8. Print bill docx

