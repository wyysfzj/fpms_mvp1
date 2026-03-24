# Batch FC6 — Dashboard Polish + Final Verification — Task Plan

> Created: 2026-02-28
> Status: Planning

## Objective
Polish dashboard KPI logic, simplify enriched tasks (use B6 client_name), run final verification.

## Backend Dependency Check
- **All previous batches (A0-B6, FA0-FC5)**: COMPLETE

## Pre-existing Implementation
- `fetchDashboardKpi()`: already uses `.total` from pagination responses
- `ActionCenter.vue`: already shows `client_name` in task rows (line 27)
- `EnrichedTask` interface: already has `client_name` (line 49)
- `fetchEnrichedTasks()`: fetches cases to resolve client_names — UNNECESSARY since B6 adds client_name to task responses

## Still Needed
- Simplify `fetchEnrichedTasks()` to use `task.client_name` directly (remove getCases batch-fetch)
- Fix `fetchPipelineKpi()` unallocated payments metric
- Possibly optimize urgent task counting
- Dashboard.vue: minor polish if needed
- Final quality gate

## File Allowlist (STRICT)
| File | Action |
|------|--------|
| `frontend/src/modules/dashboard/dashboard.api.ts` | MODIFY |
| `frontend/src/modules/dashboard/pages/Dashboard.vue` | MODIFY |
| `frontend/src/modules/dashboard/components/ActionCenter.vue` | MODIFY |

## Tasks
- T1: Architect Plan
- T2: Optimize dashboard.api.ts
- T3: Polish Dashboard.vue (if needed)
- T4: Polish ActionCenter.vue (if needed)
- T5: Quality Gate
- T6: Review Report
