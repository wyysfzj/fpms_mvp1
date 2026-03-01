# AI‑EOS PROMPT — FE‑1‑01
## Title
FE‑1‑01: App Shell (Sidebar + Header + Main Scroll) aligned to reference UI

## Context
Repo: FPMS MVP1 frontend (Vue3 + TS + Vite + Pinia + Element Plus).
You must implement the UI shell to match the provided reference HTML and design tokens spec:
- Reference layout & behaviors: `reference/case_detail.html`
- Source-of-truth tokens spec: attached `fpms.css` (requires `src/styles/variables.css` to match EXACT values)

## Objective
Implement a reusable, token-driven application shell:
1) Sidebar navigation using Element Plus `el-menu` (or equivalent), styled to match reference hover/active states.
2) Header (height 60px) with breadcrumb/title, search pill (can be placeholder), and user menu (logout).
3) Main content area with scroll and consistent padding (30px).
4) Must respond to `body.mode-immersive` by collapsing sidebar/header via CSS variables and hiding overflow, aligned to reference.

## Non‑Goals (hard constraints)
- Do NOT implement RBAC logic (FE‑1‑02).
- Do NOT implement global error pages (FE‑1‑03).
- Do NOT implement Focus Mode toggle/store (FE‑1‑04) beyond ensuring layout *responds* to `body.mode-immersive`.
- Do NOT add heavy dependencies.

## File Allowlist (ONLY modify/add these)
- `src/layout/MainLayout.vue`
- `src/App.vue`
- `src/router/index.ts` (ONLY if needed to ensure MainLayout is used for authenticated routes)
- `src/components/layout/*` (new)
- `src/components/nav/*` (new; only structural components, no RBAC logic)
- `src/components/header/*` (new)
- `src/styles/variables.css` (new or align; MUST match fpms.css token block exactly)
- `src/styles/base.css` (if needed)
- `src/styles/layout.css` (new; app shell layout rules aligned to reference)
- `src/main.ts` (ONLY if needed to import global styles)
- `index.html` (ONLY if fonts are not already loaded; load Inter / Noto Serif SC / JetBrains Mono)
- Evidence Log:
  - `task/frontend/FE-1/FE-1-01_evidence.md` (add)

If additional files seem required, STOP and propose a smallest atomic fix task with its own allowlist.

## Implementation Requirements

### A) Tokens file: `src/styles/variables.css`
You MUST include this block exactly (values and names). Do not change them:

```css
:root {
  --color-primary: #2563EB;
  --color-success: #10B981;
  --color-danger: #EF4444;

  --color-bg-body: #F1F5F9;
  --color-bg-panel: #FFFFFF;
  --color-bg-sidebar: #FFFFFF;

  --font-main: "Inter", "PingFang SC", system-ui, sans-serif;
  --font-read: "Inter", "PingFang SC", system-ui, sans-serif;

  --sidebar-width: 240px;
  --header-height: 60px;
  --radius-base: 6px;
  --shadow-card: none;
  --border-panel: 1px solid #E2E8F0;
}

body.mode-immersive {
  --color-primary: #0D9488;

  --color-bg-body: #F5F5F4;
  --color-bg-panel: #F5F5F4;
  --color-bg-sidebar: transparent;

  --font-read: "Noto Serif SC", "Songti SC", serif;

  --sidebar-width: 0px;
  --header-height: 0px;
  --shadow-card: none;
  --border-panel: none;
}
```

Notes:
- You MAY add *additional* variables in other CSS files (e.g. layout.css) if needed, but do not modify the above values.
- Prefer to define any aliases (e.g. `--color-border`, `--text-main`) outside the exact block to preserve spec.

### B) Element Plus variable mapping
In a global CSS file (base.css or layout.css), map tokens to Element Plus CSS variables minimally:
- `--el-color-primary: var(--color-primary);`
- `--el-border-radius-base: var(--radius-base);`
- `--el-border-color: #E2E8F0;` (or derived from border-panel)
- Ensure background/text colors are coherent with tokens.

### C) App Shell layout CSS (aligned to reference)
Implement the shell with these behaviors:
- Root uses a “sidebar + main container” layout:
  - Sidebar width: `var(--sidebar-width)`
  - Header height: `var(--header-height)`
  - Main content scroll area with padding 30px
- Under `body.mode-immersive`:
  - Sidebar/header collapse because width/height variables become 0px
  - Content padding changes to “paper-like reading” (e.g. `40px 15% 0 15%`), aligned to reference

Avoid inline styles: use classes.

### D) Components
- `MainLayout.vue` orchestrates:
  - `<SidebarNav />`
  - `<TopHeader />`
  - `<router-view />`
- Sidebar uses `el-menu` (or list) but must visually match:
  - hover background similar to `#F8FAFC`
  - active background similar to `#EFF6FF`
  - active text uses primary color

### E) Router usage
- Ensure authenticated routes render inside `MainLayout` (typically via nested routes).
- Login route should NOT use `MainLayout`.

## Quality Gates (mandatory)
Run:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log (mandatory)
Write `task/frontend/FE-1/FE-1-01_evidence.md` including:
- Commands executed + key success outputs
- Screens you manually verified:
  - Sidebar visible in normal mode
  - Header height 60px in normal mode
  - Adding `mode-immersive` class to `<body>` collapses sidebar/header and changes content padding

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence Log path
