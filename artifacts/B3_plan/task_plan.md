# B3 — Document→FeeDraft Linking — Task Plan

## Status: READY FOR IMPLEMENTATION

## Batch Scope
When a document is registered with a DocTemplate that has `fee_draft_type` configured,
auto-create a FeeDraft linked to the case. Interface-first — if template has no
fee_item_list, just create an empty draft.

## Team Composition
| Role | Agent Name | Status |
|------|-----------|--------|
| Architect | architect | ✅ Plan Complete |
| Backend Impl | backend-impl | Pending |
| Test Agent | test-agent | Pending |
| Reviewer | reviewer | Pending |

## Task Decomposition

### B3-1: Create `fee_linking_service.py` (Backend Agent)
- **File**: `backend/app/modules/documents/fee_linking_service.py` (NEW)
- **Function**: `maybe_create_fee_draft(db, document, template) -> FeeDraft | None`
- Check `template.fee_draft_type` — if None, return None
- Load Case via `db.get(Case, document.case_id)` for `client_id`
- Create FeeDraft: case_id, client_id from case, draft_type=template.fee_draft_type, currency="CNY"
- Parse `template.fee_item_list` (JSON) → create FeeItem rows if valid
- On malformed JSON → `logger.warning()`, skip items, still return draft
- Does NOT commit — caller handles commit
- **Helper**: `_parse_and_create_fee_items()` for JSON parsing logic

### B3-2: Wire into `create_document` API endpoint (Backend Agent)
- **File**: `backend/app/modules/documents/api.py` — modify `create_document`
- Add imports: `select`, `DocTemplate`, `maybe_create_fee_draft`
- After `create_document_service()`, before task generation:
  - Re-load template via `db.execute(select(DocTemplate)...)`
  - Call `maybe_create_fee_draft(db, document, template)`
  - Store draft_id if created
- After `db.commit()`: set `X-Auto-Fee-Draft-Created: {draft_id}` header
- Follows same pattern as existing `X-Auto-Tasks-Created`

### B3-3: Write tests (Test Agent)
- **File**: `backend/tests/test_b3_fee_linking.py` (NEW)
- 7 test cases covering:
  1. GRANT_NOTICE → FeeDraft created + header
  2. FeeDraft fields correct (type, currency, status, totals)
  3. client_id inherited from case
  4. No template → no draft
  5. CLIENT_IN template (no fee_draft_type) → no draft
  6. fee_item_list JSON → FeeItems created
  7. Malformed fee_item_list → no crash, draft still created

## Dependencies
```
B3-1 → B3-2 → B3-3 (sequential)
```
Backend Agent does B3-1 then B3-2, then Test Agent does B3-3.

## Files Modified
| File | Action | Lines |
|------|--------|-------|
| `backend/app/modules/documents/fee_linking_service.py` | CREATE | ~80 |
| `backend/app/modules/documents/api.py` | MODIFY | ~15 added |
| `backend/tests/test_b3_fee_linking.py` | CREATE | ~200 |

## Quality Gate
```bash
cd backend
ruff check --fix . && ruff format .
pytest tests/test_b3_fee_linking.py -v
pytest --tb=short
```
