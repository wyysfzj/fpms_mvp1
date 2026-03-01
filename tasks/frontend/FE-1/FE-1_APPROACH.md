# Phase FE‑1: Layout + Navigation + Global Error UX — Approach

## Scope & Goal
Phase FE‑1 establishes the **application shell**, **navigation**, and **global error UX** on top of the FE‑0 foundation (auth/session + API client).

Deliverables:
1) **Modern law-firm grade App Shell** (Sidebar + Header + Main Scroll Area) using Element Plus + strict CSS tokens.
2) **RBAC-aware navigation (best-effort)**: show/hide menu items based on available permissions; always rely on backend 403 as source of truth.
3) **Global error UX**: consistent handling for 401/403/422/409, with requestId display.
4) **Focus Mode infrastructure**: dual-mode UI (Work Mode vs Immersive/Focus Mode) aligned to the provided reference HTML + design tokens.

## UI Style — Non-Negotiable Source of Truth
- **Design tokens & dual-mode spec** must be implemented exactly as described in the attached `fpms.css` (the spec explicitly states `src/styles/variables.css` must match).  
- **Visual/interaction reference** is the provided `case_detail.html`: layout structure, spacing, header height (60px), sidebar width (240px), pill search, and floating mode toggle behavior.

## Architectural Principles (FE‑1)
- Use **CSS variables (tokens) as the single source** for sizes/colors/typography.
- Avoid inline styles and magic numbers in Vue SFC templates. Prefer `class` + token-driven CSS.
- Prefer Element Plus components, but **override their look via CSS variables** (mapping tokens to Element Plus vars).
- Global error routing must avoid circular imports: prefer **DOM CustomEvent** (“fpms:forbidden”) + a single listener in `main.ts`.

## Task Order (Atomic, PR-sized)
Execute tasks in this order:

### FE‑1‑01 — App Shell (Layout)
- Build/align `MainLayout.vue` to match reference:
  - Sidebar (el-menu) with hover/active states
  - Header (60px) with breadcrumbs + search pill + user menu
  - Scrollable main content with default padding (30px)
  - Works under `body.mode-immersive` (sidebar/header collapse via tokens and CSS rules)

### FE‑1‑02 — RBAC Navigation
- Centralize menu definitions and required permissions.
- Render menu items based on permissions (best-effort).
- Keep UI styling consistent with tokens (hover/active colors from variables, not hard-coded).

### FE‑1‑03 — Global Error UX
- Add `PermissionDenied` and `NotFound` pages.
- Global 403 handling via event (with required_perm + requestId).
- Standard error banner component used by pages.

### FE‑1‑04 — Focus Mode Infrastructure
- Pinia UI store: `work` vs `immersive` mode; persist in localStorage.
- Body class toggling (`mode-immersive`).
- Floating toggle component styled like reference; visible only on routes that opt-in via `meta.supportsFocusMode`.

## Evidence Requirements (AI‑EOS)
Every task must:
- Limit edits to its allowlist.
- Run and log: `npm run lint`, `npm run typecheck`, `npm run build`.
- Produce an evidence markdown under `task/frontend/FE-1/`.
