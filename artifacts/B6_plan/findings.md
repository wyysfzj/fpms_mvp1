# B6 Findings

## Bugs Found
_None_

## Deviations from Plan
_None_

## Discoveries

### 1. Task list uses raw dicts, not Pydantic schemas
The `GET /tasks` endpoint (tasks/api.py:110) returns `dict[str, Any]` and builds items as inline dicts (lines 146-164), NOT using `TaskListItemOut` schema. This means adding `client_name` is simply adding a new key to the dict — no schema change needed for tasks.

However, `GET /tasks/today` DOES use `TaskListItemOut` (tasks/api.py:197-209). The B6 scope only targets `GET /tasks`, not `GET /tasks/today`.

### 2. Document list constructs DocumentOut explicitly
The `get_documents()` endpoint (documents/api.py:162-179) constructs each `DocumentOut` field-by-field, NOT via `model_validate`. This means we must add `case_no=...` explicitly in the constructor call.

### 3. Document model has `case` relationship defined
`Document.case` relationship exists (documents/models.py:75), but the list endpoint does NOT eager-load it. Using batch-resolve (separate query) is more efficient and consistent with the existing tasks pattern.

### 4. No migration needed
All B6 changes are application-level Python code. No new database columns, no new tables. The `case_no` and `client_name` fields are resolved at query time via batch lookups.

### 5. Imports already available
- `tasks/api.py` already imports both `Case` and `Client` (lines 15-15)
- `documents/service.py` already imports `Case` (line 12)
- `documents/api.py` does NOT import `Case` — needs to be added

### 6. Session-scoped test fixtures
The test DB uses session-scoped fixtures (conftest.py). Test data created by one test persists. Tests should use unique identifiers (uuid4) to avoid collisions.
