# Batch FA2 — List UX Polish — Task Plan

> **Team**: fa2-batch
> **Date**: 2026-02-26
> **Goal**: Add missing filter controls to list pages. Wire to existing API query params.

---

## Batch Summary

- **Batch**: FA2 (List UX Polish)
- **Backend Dependency**: None — uses existing filter params
- **File Allowlist** (strict — 4 files, all MODIFY):
  1. `frontend/src/modules/documents/pages/DocumentList.vue`
  2. `frontend/src/modules/tasks/pages/TaskList.vue`
  3. `frontend/src/modules/billing/pages/BillList.vue`
  4. `frontend/src/modules/fees/pages/FeeDraftList.vue`

## Changes Per Page

1. **DocumentList** — Add `el-select` direction filter (全部/收文 IN/发文 OUT)
2. **TaskList** — Add `el-select` status filter (全部/OPEN/IN_PROGRESS/COMPLETED/CANCELLED)
3. **BillList** — Add `el-select` status filter (全部/ISSUED/PAID/VOID)
4. **FeeDraftList** — Add `el-select` status filter (全部/OPEN/LOCKED)

## API Wrapper Status (all ready)

- `getDocuments({ direction })` — ✅ supported
- `getTasks({ status })` — ✅ supported
- `getBills({ status })` — ✅ supported
- `getFeeDrafts({ status })` — ✅ supported

## Pattern (from Claude_FE_enhance.md)

```html
<el-row :gutter="16" style="margin-bottom: 16px">
  <el-col :span="6">
    <el-select v-model="filterX" placeholder="全部" clearable @change="fetchList">
      <el-option label="全部" value="" />
      <el-option label="X" value="X" />
    </el-select>
  </el-col>
</el-row>
```

## Dependency Graph

```
T1 (Architect Plan) ──┐
T2 (Backend Verify) ──┼──→ T3 (Frontend Impl) ──→ T4 (Test) ──→ T5 (Review)
```
