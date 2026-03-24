# Batch FB1 — Task Detail Page + TaskLog View — Task Plan

> **Team**: fb1-batch
> **Date**: 2026-02-27
> **Goal**: Create the missing `/tasks/:id` detail page. Display task metadata, status actions, and audit log (from backend A1's `GET /tasks/{id}/logs` API).

---

## Batch Summary

- **Batch**: FB1 (Task Detail Page + TaskLog View)
- **Backend Dependency**: Backend Batch A1 (TaskTemplate + TaskLog) — MUST verify
- **File Allowlist** (strict — 5 files):
  1. `frontend/src/api/tasks.ts` (MODIFY)
  2. `frontend/src/api/tasks.types.ts` (MODIFY)
  3. `frontend/src/modules/tasks/pages/TaskDetail.vue` (NEW)
  4. `frontend/src/modules/tasks/components/TaskLogTimeline.vue` (NEW)
  5. `frontend/src/router/index.ts` (MODIFY)

## Changes Summary

1. **tasks.types.ts** — Add `TaskLog` type, verify `Task` type has all detail fields
2. **tasks.ts** — Add `getTask(id)`, `getTaskLogs(taskId)` API wrappers
3. **TaskDetail.vue** — Full detail page with el-tabs (Overview + Audit Log), status actions
4. **TaskLogTimeline.vue** — el-timeline component for audit log entries
5. **router/index.ts** — Add `/tasks/:id` route

## Dependency Graph

```
T1 (Architect Plan) ──┐
T2 (Backend Verify) ──┼──→ T3 (Frontend Impl) ──→ T4 (Test) ──→ T5 (Review)
```

## Tasks

| # | Task | Agent | Blocked By |
|---|------|-------|------------|
| T1 | Architect Review + Plan | architect-agent | — |
| T2 | Backend A1 API Verify | backend-agent | — |
| T3 | Frontend Implementation | frontend-agent | T1, T2 |
| T4 | Test Verification | test-agent | T3 |
| T5 | Review Report | reviewer-agent | T3, T4 |
