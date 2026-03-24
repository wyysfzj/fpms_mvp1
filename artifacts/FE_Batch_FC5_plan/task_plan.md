# Batch FC5 — Cross-entity List Enrichment — Task Plan

> Created: 2026-02-28
> Status: Planning

## Objective
Display client_name in TaskList, ensure case_no in DocumentList, add client_id filter to both lists.

## Backend Dependency Check
- **Backend B6 Status**: COMPLETE
  - GET /tasks returns client_name (batch-resolved Case→Client join)
  - GET /documents returns case_no (already mapped)
  - Both accept client_id query filter parameter

## Pre-existing Implementation
- `documents.types.ts`: Document already has `case_no?: string`
- `documents.ts`: BackendDocument has `case_no`, mapDocument maps it
- `DocumentList.vue`: Already shows case_no column (line 62-68)

## Still Missing
- `tasks.types.ts`: No `client_name` on Task; No `client_id` on TaskListParams
- `tasks.ts`: BackendTask missing `client_name`; mapTask doesn't map it; getTasks doesn't pass client_id
- `documents.types.ts`: No `client_id` on DocumentListParams
- `documents.ts`: getDocuments doesn't pass client_id
- `TaskList.vue`: No client_name column; no client_id filter
- `DocumentList.vue`: No client_id filter

## File Allowlist (STRICT)
| File | Action |
|------|--------|
| `frontend/src/api/tasks.types.ts` | MODIFY |
| `frontend/src/api/documents.types.ts` | MODIFY |
| `frontend/src/modules/tasks/pages/TaskList.vue` | MODIFY |
| `frontend/src/modules/documents/pages/DocumentList.vue` | MODIFY |

**Implicit scope (same pattern as FC3/FC4):**
| `frontend/src/api/tasks.ts` | MODIFY — BackendTask + mapTask + getTasks |
| `frontend/src/api/documents.ts` | MODIFY — getDocuments client_id param |

## Tasks
- T1: Architect Plan
- T2: Update tasks.types.ts + documents.types.ts
- T3: Update tasks.ts + documents.ts mappers
- T4: Update TaskList.vue — add client_name column + client_id filter
- T5: Update DocumentList.vue — add client_id filter
- T6: Quality Gate
- T7: Review Report

## Dependency Graph
```
T1 → T2 (types) → T3 (mappers) → T4 + T5 (parallel) → T6 (QA) → T7 (Review)
```
