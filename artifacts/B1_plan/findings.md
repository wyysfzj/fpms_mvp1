# B1 Batch — Findings

## Initial Analysis
- DocTemplate model existed with only 4 fields (code, name, direction, enabled)
- Zero DocTemplate schemas, service functions, API endpoints, or permissions existed
- No seed data or test coverage for doc templates

## Implementation Notes
- `DocumentDirection` enum already existed in `documents/enums.py` — reused for schema validation
- Route ordering confirmed correct: `/doc-templates` registered before `/documents/{document_id}` in api.py
- Test conftest needed `from app.models import *` import to populate SQLAlchemy registry (pre-existing issue with relationship resolution)
- Migration chain: `a3_case_fields_01` → `b1_doc_tpl_01`

## Bugs Found
- None in B1 scope
- Pre-existing: conftest.py needed full model import to resolve SQLAlchemy `Case` relationship (fixed in T8)
