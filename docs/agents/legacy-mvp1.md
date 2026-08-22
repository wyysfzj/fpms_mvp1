# FPMS Legacy MVP1 Routing

This module applies only to matching legacy task paths; it does not broaden a modern task.

### Rule GOV-LEGACY-001 — Phase and one-time router compatibility

Phase 3 domain API work makes no schema or Alembic changes except explicitly requested
Phase 0-EXT compatibility fixes, uses existing ORM models, implements endpoints in the
module `api.py`, and preserves response envelopes. Phase 3.1 has the same constraints and
only implements `tasks/backend/apis_ext/**`. Phase 3.5 is service-layer logic with no schema
change; docxtpl rendering, context builders, and Document-to-Task generation are allowed,
while API wiring changes only when the exact task requires them.

Router wiring is module-level and one-time. Do not rewire an already wired module. Add
`include_router(...)` only when entering a module for the first time, and limit changes to
`backend/app/api/router.py` unless the exact task authorizes another path. Legacy task-path
routing never overrides current exact closure, allowlist, safety, evidence, or release
rules.

Rule-Ref: GOV-API-UI-001
Rule-Ref: GOV-SCOPE-001
