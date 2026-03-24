# DEMO-QA-CASE-01 Summary

## Scope
Verification only for the case edit update flow after:
- backend stopgap for empty-string date handling
- backend typed update schema/service migration
- frontend payload normalization
- frontend case edit page alignment

## Commands
- `lint`: `cd backend && ruff check app/modules/cases/api.py app/modules/cases/schemas.py app/modules/cases/service.py && cd ../frontend && npm run typecheck`
- `test`: `cd backend && PYTHONPATH=. python3 /tmp/demo_qa_case_testclient.py`

## Results
- Contract/gate check passed.
- Smoke verification passed with `TestClient`.
- Valid update payload returned `200`.
- Invalid status payload using `status=\"ACCEPTED\"` returned `422`.
- Empty optional dates in the valid payload no longer caused `500`.

## Additional Finding
- The demo case currently stored in the database still contains legacy invalid status data: `ACCEPTED`.
- Because the backend now validates status through the typed schema, replaying that legacy value correctly fails with `422`.
- The successful smoke therefore used a valid update payload that omitted `status`, while the negative smoke explicitly verified `ACCEPTED -> 422`.

## Expected Status Codes
- `PUT /api/v1/cases/{id}` with supported fields: `200`
- `PUT /api/v1/cases/{id}` with invalid `status`: `422`
- Empty optional date fields: no `500`
