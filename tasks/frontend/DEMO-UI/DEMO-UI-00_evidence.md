# Evidence Log — DEMO-UI-00

## Task
- ID: DEMO-UI-00
- Title: Style-B 主题应用 + VITE_DEMO_UI 开关
- Date: 2026-02-10
- Agent/Model: Claude Opus 4.6

## File Allowlist
- ✅ Confirmed all changes are within allowlist
- `frontend/.env.example` — modified (added VITE_DEMO_UI comment)
- `frontend/src/styles/demo-themes.css` — **new** (style-b CSS variable overrides)
- `frontend/src/stores/ui.ts` — modified (added demoUI computed, applyDemoTheme())
- `frontend/src/main.ts` — modified (import demo-themes.css)

## Commands Executed
```bash
cd frontend
npm run lint       # ✅ pass
npm run typecheck  # ✅ pass
npm run build      # ✅ pass (built in 2.93s)
```

## Key Outputs
- lint: no warnings/errors
- typecheck: no errors (vue-tsc --noEmit)
- build: ✓ 1631 modules transformed, built in 2.93s

## Changes Summary

### demo-themes.css (new)
- Extracted style-b CSS variables from `reference/patent_ui.html` lines 129-166
- Mapped patent_ui variable names to project's actual variable names:
  - `--bg-body` → already `--color-bg-body` (same value #F1F5F9, no override needed)
  - `--text-sub` → `--text-sub` (#64748B → #94A3B8, overridden)
  - `--sidebar-width` → `--sidebar-width` (240px → 220px, overridden)
  - `--border-color` → `--color-border` (#E2E8F0 → #F1F5F9, overridden)
- Added new tokens: `--sidebar-active-bg`, `--sidebar-active-text`, `--content-padding`, `--card-padding`, `--table-row-padding`, `--radius-card`, `--text-highlight`, `--font-num`
- Added status tag classes: `.tag-urgent`, `.tag-warning`, `.tag-normal`
- All under `body.style-b` selector — zero impact when class absent

### ui.ts
- Added `DEMO_UI` const from `import.meta.env.VITE_DEMO_UI`
- Added `demoUI` computed getter (exposed to components)
- Added `applyDemoTheme()` method — adds/removes `style-b` class on body
- Called at store init alongside `applyBodyClass()`

### main.ts
- Added `import './styles/demo-themes.css'` after other style imports

### .env.example
- Added commented `VITE_DEMO_UI=1` with description

## Manual Verification
### Steps
1. With `VITE_DEMO_UI=1` in `.env`: body should have class `style-b`
2. Without `VITE_DEMO_UI`: body should NOT have class `style-b`
3. Work/immersive mode toggle should still function independently

### Results
- Gates: PASS (lint + typecheck + build all clean)
- Code review: all changes within allowlist, no variables.css base tokens modified

## UI Reference Alignment Notes
- `reference/patent_ui.html` alignment: style-b CSS variables faithfully extracted and mapped
- Tokens safety (variables.css base block unchanged): ✅ — verified file not in git diff for this task
- Simplified from original spec: no A/B/C switching, no DemoToolbar — only style-b applied via env flag

## Notes
- The base theme values in `variables.css` already closely match style-b (same `--color-bg-body`, `--color-bg-panel`, `--color-primary`). Only 3 overrides needed plus new tokens for future dashboard/relation components.
