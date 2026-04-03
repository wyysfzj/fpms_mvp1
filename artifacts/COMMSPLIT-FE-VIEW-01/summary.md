# COMMSPLIT-FE-VIEW-01 Evidence Summary

## Task
- ID: `COMMSPLIT-FE-VIEW-01`
- Runbook: `tasks/postenhancement/frontend/COMMSPLIT-FE-VIEW-01.md`

## Scope Compliance
- Product changes stayed inside the claimed closure slice.
- Product file modified:
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
- No editing, settlement exposure, list exposure, router/menu, backend, or API/types files were modified by this task.
- Pre-existing dirty API files remained outside this task and were recorded in `baseline_external_files.txt`:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`

## Exact Closure Slice
- implement case detail split viewing only

## Implemented Behavior
- `CaseDetail.vue` now exposes a read-only `代理人分摊` section when `agent_splits` exist.
- The detail page shows split rows with agent, role, and share ratio.
- `agent_splits` becomes the primary split viewing carrier on the detail page, while `主办代理人 / 辅办代理人` remain in `代理人分配` as context.
- Unknown role codes are not surfaced verbatim; only Simplified Chinese or placeholder text is shown.

## Verification
- `cd frontend && npm run lint -- src/modules/cases/pages/CaseDetail.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh COMMSPLIT-FE-VIEW-01`

## Non-Closure
- does not close editing
- does not close settlement exposure
- does not close list exposure
- does not close router/menu changes
- does not close backend/API/types changes
