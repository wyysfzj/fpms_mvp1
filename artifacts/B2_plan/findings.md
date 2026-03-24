# B2 Findings — Architect Agent

## Codebase Audit Findings

### 1. DocumentOut uses manual construction, not model_validate
**Location**: `documents/api.py` lines 158-172, 230-241, 315-337, 375-386
**Impact**: Every new field added to DocumentOut requires updating 4 separate places in api.py
**Recommendation**: Consider refactoring to use `DocumentOut.model_validate(document)` with `ConfigDict(from_attributes=True)` in a future batch. For B2, follow existing pattern (manual construction) to minimize blast radius.

### 2. Template variable scoping in create_document()
**Location**: `documents/service.py` line 81-88
**Impact**: The `template` variable is only defined inside `if data.doc_template_id:` block, making it inaccessible for cascade logic.
**Fix**: Restructure to `template = None` before the if-block. This is a safe change.

### 3. TaskAction enum missing AUTO_WRITEOFF
**Location**: `tasks/enums.py`
**Impact**: B2 needs AUTO_WRITEOFF for task log entries. Also adding STATUS_CHANGE for template cascade traceability.
**Note**: The action field in TaskLog is String(32), not an enum column — so adding enum values is backward-compatible.

### 4. No circular import risk
**Verified**: tasks/models.py does NOT import from documents. documents/models.py does NOT import from tasks. The dependency is one-directional: documents/service.py will import Task model and task service helpers. This is safe.

### 5. _create_task_log is a module-level function (not class method)
**Location**: `tasks/service.py` line 47-65
**Impact**: Can be imported directly as `from app.modules.tasks.service import _create_task_log`. Despite the underscore prefix, it's a stable utility function used throughout the tasks module.

### 6. close_task() commits independently
**Location**: `tasks/service.py` line 222-242
**Impact**: Cannot use close_task() from within create_document() because it calls db.commit() independently, which would interfere with the document creation transaction. Must implement auto write-off inline using direct attribute mutation + _create_task_log().

## B1 Dependency Status: ALL PRESENT
- DocTemplate model SPEC fields: verified
- DocTemplate schemas: verified
- DocTemplate CRUD service + API: verified
- B1 migration: verified
- Test seed data (OA_IN, OA_OUT, OA_REPLY): verified
