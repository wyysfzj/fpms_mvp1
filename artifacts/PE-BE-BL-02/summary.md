# PE-BE-BL-02

Status: PASS

Atomic Task File:
- `tasks/postenhancement/backend/PE-BE-BL-02.md`

Covered Items:
- `US-BL-06`
- `FR-BL-07`
- `FR-BL-08`

Exact Closure Slice:
- `GET /dunning/{id}` detail endpoint returning one dunning batch head, counts, and its `DunningLine` rows for the same dunning contract the frontend needs; nothing else.

Explicit Non-Closure:
- does not add any new list endpoints or reshape filters
- does not create dunning letter/document generation artifacts
- does not touch prepayment/offset visibility
- broader `billing` service diff from `artifacts/PE-BE-BL-01/baseline_allowlist.diff` remains historical and is explicitly excluded here

Incremental Implementation:
- `backend/app/modules/collections/service.py`: added `get_dunning_detail` helper to load a batch and its lines.
- `backend/app/modules/collections/api.py`: added `GET /dunning/{id}` route wired to the helper.
- `backend/tests/test_collections_e2e.py`: created `test_collections_dunning_detail_includes_lines` that generates a dunning batch then verifies the new endpoint returns the requested lines.

Dirty Baseline Handling:
- billing service manual-bill diffs were already present before this task and are non-closure noise recorded under `artifacts/PE-BE-BL-02/baseline_allowlist.diff`; the acceptance claims only the new detail endpoint delta.

Validation:
- `ruff check backend/app/modules/collections/api.py backend/app/modules/collections/service.py backend/app/modules/billing/service.py backend/tests/test_collections_e2e.py`
- `cd backend && pytest -q tests/test_collections_e2e.py -k 'dunning or bad_debt'`

Notes:
- no schema/migration changes
- no Batch 5 spillover
- direct service/read capability only
