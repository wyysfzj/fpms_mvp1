# AI‑EOS PROMPT — FE‑1‑02
## Title
FE‑1‑02: RBAC-aware navigation (best-effort) with token-aligned styling

## Context
FE‑1‑01 App Shell exists. Now implement navigation configuration and permission-aware menu rendering.
Backend is source of truth; frontend can do best-effort menu hiding if permissions are available.

## Objective
1) Centralize menu definition (items, routes, icons, requiredPerms).
2) Render Sidebar menu based on `auth.perms` when available:
   - If perms unknown/empty: do not hide (show all).
3) Keep the menu styling aligned to tokens and the reference UI.

## Non‑Goals
- Do NOT implement global error pages (FE‑1‑03).
- Do NOT implement focus mode toggle/store (FE‑1‑04).
- Do NOT add dependencies.

## File Allowlist (ONLY modify/add these)
- `src/constants/perms.ts` (new)
- `src/constants/menu.ts` (new)
- `src/stores/auth.ts` (ONLY if needed to expose perms safely; no router imports)
- `src/components/nav/SidebarNav.vue`
- `src/router/index.ts` (ONLY to add route meta like `requiredPerms`, if needed)
- `src/styles/layout.css` (ONLY for menu styling refinements using tokens)
- Evidence Log:
  - `task/frontend/FE-1/FE-1-02_evidence.md` (add)

If additional files seem required, STOP and propose a smallest atomic fix task.

## Implementation Requirements
### A) Permission strategy (best-effort)
- `auth.perms` may be:
  - `string[]` (available)
  - `null`/`undefined` (unknown)
- Menu display logic:
  - If perms unknown → show all menu items
  - Else show items where `requiredPerms` is empty OR intersects with `auth.perms`

### B) Route meta (optional but recommended)
- Add `meta.requiredPerms?: string[]` to routes (for FE‑1/FE‑2 use).
- Do NOT block navigation purely client-side if perms are unknown; rely on backend 403.

### C) SidebarNav styling
- Use classes + tokens.
- Active/hover colors must match reference:
  - hover background ~ `#F8FAFC`
  - active background ~ `#EFF6FF`
  - active text uses `var(--color-primary)`
- Avoid inline styles.

## Quality Gates
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log
Write `task/frontend/FE-1/FE-1-02_evidence.md`:
- Commands + key outputs
- Manual checks:
  - With perms unknown: all menu items show
  - With perms mocked in store: restricted items hide (best-effort)
  - Menu hover/active styling matches tokens

## Output in final response (no extra suggestions)
- Summary
- Commands
- Evidence path
