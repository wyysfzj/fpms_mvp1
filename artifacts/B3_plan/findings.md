# B3 Findings

## Bugs Found
_None_

## Deviations from Plan
_None yet_

## Discoveries

### 1. Case model has no currency field
- `Case` model (`cases/models.py`) has no `currency` column
- FeeDraft requires `currency` — default to `"CNY"` (matches FeeDraft server_default)
- Future enhancement: could pull from system param or client settings

### 2. GRANT_NOTICE template already seeded with fee_draft_type
- `conftest.py:147-149` seeds `GRANT_NOTICE` with `fee_draft_type="GRANT_FEE"`
- No additional test data seeding needed for basic positive test
- But fee_item_list is NOT set on GRANT_NOTICE — need a custom template for item parsing tests

### 3. FeeItem.rate_id is nullable
- `FeeItem.rate_id` is `nullable=True` (`fees/models.py:48-49`)
- Auto-created FeeItems from fee_item_list can safely have `rate_id=None`
- Existing `add_fee_item()` in fees/service.py requires rate_id, but we bypass that service

### 4. API layer two-phase commit pattern
- `create_document` endpoint does: service commit → task generation → second commit
- Fee draft creation slots in between service commit and task generation
- Both fee draft and tasks get committed in the second `db.commit()`

### 5. Template re-query is necessary but lightweight
- `create_document_service()` loads template internally but doesn't return it
- API layer must re-query template by `document.doc_template_id`
- After service commit, SQLAlchemy expires objects, so `db.get()` will hit DB
- This is a PK lookup — negligible performance impact

### 6. select import already used in api.py indirectly
- `api.py` doesn't directly import `select` — needs to be added
- `DocTemplate` is not imported in api.py — needs to be added
