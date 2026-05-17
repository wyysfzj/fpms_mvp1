# Product Sidebar Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved product sidebar navigation design with default work navigation, module navigation, and persistent collapse behavior.

**Architecture:** Keep the change frontend-only. Extend the existing menu constants and UI store, then update the existing `SidebarNav.vue` and sidebar CSS to render two navigation modes while preserving current router links and permission filtering.

**Tech Stack:** Vue 3, TypeScript, Pinia, Vue Router, Element Plus styling conventions, existing FPMS CSS variables.

---

## Atomic Task

- Task file: `tasks/frontend/FE-PRODUCT-SIDEBAR-NAV-01.md`
- Runbook: `P0-frontend-heavy-story`
- Executor role: main-thread frontend worker

## File Structure

- Modify `frontend/src/constants/menu.ts`
  - Add product navigation mode and richer menu section definitions.
  - Preserve `MENU_GROUPS` and `MENU_ITEMS` compatibility where possible.
- Modify `frontend/src/stores/ui.ts`
  - Add persistent `navMode` and `sidebarCollapsed` state.
- Modify `frontend/src/components/nav/SidebarNav.vue`
  - Render work/module nav switch, collapsible sidebar, permission-filtered sections, and active route states.
- Modify `frontend/src/styles/layout.css`
  - Add product sidebar layout styles and collapsed-state styles.
- Modify `frontend/src/constants/labels.zh.ts`
  - Only add shared Chinese labels if the component needs centralized display text.

## Task 1: Product Sidebar Navigation Shell

**Files:**
- Modify: `frontend/src/constants/menu.ts`
- Modify: `frontend/src/stores/ui.ts`
- Modify: `frontend/src/components/nav/SidebarNav.vue`
- Modify: `frontend/src/styles/layout.css`
- Modify: `frontend/src/constants/labels.zh.ts`
- Create: `tasks/frontend/FE-PRODUCT-SIDEBAR-NAV-01.md`
- Evidence: `artifacts/FE-PRODUCT-SIDEBAR-NAV-01/**`

- [x] **Step 1: Freeze the atomic task**

Run:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/frontend/FE-PRODUCT-SIDEBAR-NAV-01.md
```

Expected: `Atomic task check PASS`

- [x] **Step 2: Initialize evidence**

Run:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py init FE-PRODUCT-SIDEBAR-NAV-01 --task-file tasks/frontend/FE-PRODUCT-SIDEBAR-NAV-01.md --allowlist frontend/src/constants/menu.ts --allowlist frontend/src/stores/ui.ts --allowlist frontend/src/components/nav/SidebarNav.vue --allowlist frontend/src/styles/layout.css --allowlist frontend/src/constants/labels.zh.ts --allowlist docs/superpowers/plans/2026-05-17-product-sidebar-navigation.md --allowlist tasks/frontend/FE-PRODUCT-SIDEBAR-NAV-01.md
```

Expected: evidence initialized under `artifacts/FE-PRODUCT-SIDEBAR-NAV-01/`

- [x] **Step 3: Extend menu data**

In `frontend/src/constants/menu.ts`:

- Add `NavMode = 'work' | 'module'`.
- Add a product nav section model.
- Add `PRODUCT_NAV_GROUPS` with `work` and `module` modes.
- Preserve the existing route strings and permission arrays.
- Keep all user-facing labels in Simplified Chinese.

- [x] **Step 4: Extend UI store**

In `frontend/src/stores/ui.ts`:

- Add `navMode`, `sidebarCollapsed`, `setNavMode`, `toggleSidebarCollapsed`, and `setSidebarCollapsed`.
- Persist state in localStorage.
- Keep existing immersive mode and demo theme behavior unchanged.

- [x] **Step 5: Update sidebar component**

In `frontend/src/components/nav/SidebarNav.vue`:

- Render logo, collapse button, work/module segmented control, section labels, nav links, and bottom groups.
- Filter children using existing `authStore.hasAnyPermission`.
- Hide empty sections after permission filtering.
- Apply active styling using Vue Router route path and item route matching.
- Render compact labels/tooltips in collapsed mode.

- [x] **Step 6: Update layout CSS**

In `frontend/src/styles/layout.css`:

- Add `--sidebar-collapsed-width` fallback behavior through CSS classes.
- Preserve existing colors, borders, radii, scrollbar behavior, and immersive-mode sidebar hiding.
- Ensure collapsed mode does not overlap top header or content.

- [x] **Step 7: Run lint evidence**

Run:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd frontend FE-PRODUCT-SIDEBAR-NAV-01 lint -- npx eslint src --max-warnings 0
```

Expected: command passes with `rc=0`

- [x] **Step 8: Run test/build evidence**

Run:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py run --cwd frontend FE-PRODUCT-SIDEBAR-NAV-01 test -- bash -lc 'npm run typecheck && npm run build'
```

Expected: command passes with `rc=0`

- [x] **Step 9: Browser verification**

Use the local frontend. This worktree was verified at `http://127.0.0.1:5174/` with API base `http://localhost:8001/api/v1`:

- Confirm expanded sidebar shows `工作导航`.
- Confirm switching to `模块导航` shows module sections.
- Confirm collapse/expand changes layout and keeps active route visible.
- Confirm reload preserves nav mode and collapse state.

- [ ] **Step 10: Finalize evidence and task gate**

Run:

```bash
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py finalize FE-PRODUCT-SIDEBAR-NAV-01 --status PASS
python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FE-PRODUCT-SIDEBAR-NAV-01
./scripts/task_validate.sh FE-PRODUCT-SIDEBAR-NAV-01
```

Expected: both gates pass.

## Review Note

The plan review subagent step from `superpowers:writing-plans` is not used in this session because the active developer instruction only permits subagents when the user explicitly asks for subagent work. The implementation stays inline under the single atomic task above.
