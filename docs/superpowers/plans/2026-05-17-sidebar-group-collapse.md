# Sidebar Group Collapse Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add vertical collapse controls for large sidebar navigation groups while preserving current route visibility and the approved product navigation model.

**Architecture:** Keep the change frontend-only. Store persisted group collapse state in the existing UI Pinia store, render collapsible groups in the existing sidebar component, and add scoped layout styles in the shared layout stylesheet.

**Tech Stack:** Vue 3, TypeScript, Pinia, Vue Router, existing FPMS CSS variables.

---

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: frontend-only
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Atomic Task

- Task file: `tasks/frontend/FE-SIDEBAR-GROUP-COLLAPSE-01.md`
- Runbook: `P0-frontend-heavy-story`
- Executor role: main-thread frontend worker
- Shared-file handling: serialized in the main thread because the task touches the existing sidebar shared UI files.

## File Structure

- Modify `frontend/src/stores/ui.ts`
  - Persist sidebar group collapse state by navigation mode and group key.
- Modify `frontend/src/components/nav/SidebarNav.vue`
  - Render group headers as collapsible buttons and keep active route groups expanded.
- Modify `frontend/src/styles/layout.css`
  - Add group header, count, chevron, and collapsed group styles.
- Create `tasks/frontend/FE-SIDEBAR-GROUP-COLLAPSE-01.md`
  - Freeze exact closure slice and verification.
- Evidence under `artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/**`

## Task 1: Sidebar Group Collapse

**Files:**
- Modify: `frontend/src/stores/ui.ts`
- Modify: `frontend/src/components/nav/SidebarNav.vue`
- Modify: `frontend/src/styles/layout.css`
- Create: `tasks/frontend/FE-SIDEBAR-GROUP-COLLAPSE-01.md`
- Evidence: `artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/**`

- [x] **Step 1: Freeze the atomic task**

Run:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/frontend/FE-SIDEBAR-GROUP-COLLAPSE-01.md
```

Expected: `Atomic task check PASS`

- [x] **Step 2: Initialize evidence**

Run:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init FE-SIDEBAR-GROUP-COLLAPSE-01 --task-file tasks/frontend/FE-SIDEBAR-GROUP-COLLAPSE-01.md --allowlist frontend/src/stores/ui.ts --allowlist frontend/src/components/nav/SidebarNav.vue --allowlist frontend/src/styles/layout.css --allowlist docs/superpowers/specs/2026-05-17-sidebar-group-collapse-design.md --allowlist docs/superpowers/plans/2026-05-17-sidebar-group-collapse.md --allowlist tasks/frontend/FE-SIDEBAR-GROUP-COLLAPSE-01.md
```

Expected: evidence initialized under `artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/` with dirty baseline captured if the worktree is already dirty.

- [x] **Step 3: Add persisted group collapse state**

In `frontend/src/stores/ui.ts`:

- Add a localStorage key for sidebar group collapse state.
- Parse saved state safely.
- Add `sidebarGroupCollapsed`, `isSidebarGroupCollapsed`, `setSidebarGroupCollapsed`, and `toggleSidebarGroupCollapsed`.
- Key state as `<navMode>:<groupKey>`.

- [x] **Step 4: Render collapsible group headers**

In `frontend/src/components/nav/SidebarNav.vue`:

- Add group button markup around the existing group labels.
- Render group items only when the group is not collapsed.
- Keep all icon links visible when the whole sidebar is collapsed.
- Compute active group from the active route item.
- Default work mode groups to expanded.
- Default module mode groups to collapsed except `module-work` and the active group.

- [x] **Step 5: Add group collapse styles**

In `frontend/src/styles/layout.css`:

- Add styles for `.nav-section`, `.nav-group-button`, `.nav-group-title`, `.nav-group-count`, `.nav-group-chevron`, and `.nav-group-items`.
- Keep styling restrained and consistent with the current sidebar tokens.
- Ensure collapsed-sidebar mode still hides group headers and preserves icon spacing.

- [x] **Step 6: Run lint evidence**

Run:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd frontend FE-SIDEBAR-GROUP-COLLAPSE-01 lint -- npx eslint src --max-warnings 0
./scripts/evidence_run.sh FE-SIDEBAR-GROUP-COLLAPSE-01 lint bash -lc 'cd frontend && npx eslint src --max-warnings 0'
```

Expected: both commands pass with `rc=0`.

- [x] **Step 7: Run typecheck/build evidence**

Run:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd frontend FE-SIDEBAR-GROUP-COLLAPSE-01 test -- bash -lc 'npm run typecheck && npm run build'
./scripts/evidence_run.sh FE-SIDEBAR-GROUP-COLLAPSE-01 test bash -lc 'cd frontend && npm run typecheck && npm run build'
```

Expected: both commands pass with `rc=0`.

- [x] **Step 8: Browser verification**

Use the worktree frontend at `http://127.0.0.1:5174/`:

- Confirm `工作导航` groups are expanded by default.
- Confirm `模块导航` shows collapsed groups with group headers.
- Expand a module group and confirm its items appear.
- Reload and confirm the opened group remains open.
- Confirm active route group stays expanded.
- Collapse the whole sidebar and confirm icon links remain visible.

- [x] **Step 9: Finalize evidence and task gate**

Run:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize FE-SIDEBAR-GROUP-COLLAPSE-01 --status PASS --summary-file artifacts/FE-SIDEBAR-GROUP-COLLAPSE-01/summary.md
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FE-SIDEBAR-GROUP-COLLAPSE-01
./scripts/task_validate.sh FE-SIDEBAR-GROUP-COLLAPSE-01
```

Expected: both gates pass.

## Review Note

The plan-review subagent loop is not used because the active platform instructions only permit subagents when the user explicitly asks for subagent work.
