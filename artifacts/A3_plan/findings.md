# A3 Batch — Findings

## Critical Finding 1: API-Service Code Path Divergence
- `api.py` does NOT call `service.py` for CRUD operations
- Both `POST /cases` and `PUT /cases/{case_id}` have inline ORM code in api.py
- Service functions exist but are not wired to endpoints
- **Impact**: Must update BOTH api.py inline code AND service.py functions
- **Decision**: Update both paths, do NOT refactor to merge (out of scope)

## Critical Finding 2: PUT endpoint uses untyped dict
- `PUT /cases/{case_id}` accepts `payload: dict[str, Any]` not a Pydantic schema
- New fields must use `.get()` with current value as default
- `POST /cases/{case_id}/limited-edit` also uses untyped dict

## Finding 3: POST response is minimal
- `POST /cases` only returns 6 fields: id, case_no, case_type, patent_category, flow_dir, client_id
- Should add the 15 new fields to POST response for consistency

## Finding 4: No existing case field tests
- No `test_case_fields.py` exists
- `test_v3_workflow.py` covers status enums and basic CRUD
- Need comprehensive new test file

## Finding 5: GET /cases/export duplicates GET /cases logic
- Both endpoints have identical filter + response dict construction
- New fields must be added to BOTH endpoints
