# AI‑EOS PROMPT — FE‑1‑04
## Title
FE‑1‑04: Focus Mode infrastructure (toggle + persistence + route opt-in) aligned to reference UI

## Context
Reference UI supports dual-mode:
- Default Work Mode (Modern Tech)
- Immersive Focus Mode (`body.mode-immersive`) collapses sidebar/header and creates a centered reading flow.

Tokens spec defines:
- In immersive mode: `--sidebar-width: 0px`, `--header-height: 0px`, different `--font-read`, and background changes.

FE‑1‑04 implements the app-wide mechanism to switch modes.

## Objective
1) Add a Pinia UI store that tracks `mode: 'work' | 'immersive'` with localStorage persistence.
2) On app boot, restore mode and set/remove `body.mode-immersive`.
3) Add a floating `ModeToggle` component styled like reference (pill button, top-right, subtle hover).
4) Toggle is visible ONLY on routes with `meta.supportsFocusMode = true`.
5) Provide a small demo route/page that proves:
   - sidebar/header collapse
   - content padding changes to paper-like layout
   - read font changes (font-read)
This demo is NOT a business feature page; it is a style/system demo.

## Non‑Goals
- Do NOT build full Case Detail page (FE‑2).
- Do NOT implement editor/rich text.
- Do NOT add dependencies.

## File Allowlist (ONLY modify/add these)
- `src/stores/ui.ts` (new)
- `src/components/layout/ModeToggle.vue` (new)
- `src/layout/MainLayout.vue` (update: render ModeToggle; use route meta)
- `src/router/index.ts` (add demo route + meta.supportsFocusMode flags)
- `src/views/FocusDemo.vue` (new; minimal demo content)
- `src/main.ts` (restore mode + apply body class)
- `src/styles/layout.css` (add ModeToggle styles and immersive mode demo layout classes)
- Evidence Log:
  - `task/frontend/FE-1/FE-1-04_evidence.md` (add)

If additional files seem required, STOP and propose a smallest atomic fix task.

## Implementation Requirements
### A) Persistence
- localStorage key: `fpms_ui_mode`
- values: `work` or `immersive`

### B) Body class
- If mode === immersive => add `mode-immersive`
- Else remove it

### C) Toggle component
- Must be accessible:
  - `aria-pressed` reflects state
  - reachable by keyboard
- Visual alignment to reference:
  - fixed top-right
  - pill radius (99px)
  - border `#E2E8F0` and subtle shadow
  - hover raises slightly

### D) Route opt-in
- Demo route sets `meta.supportsFocusMode = true`
- For other routes, toggle hidden.

### E) Demo content
- Include a “two-column” layout in work mode and verify it becomes single-column in immersive mode (via CSS classes).
- Include long-form text styled with `font-read`.

## Quality Gates
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log
Write `task/frontend/FE-1/FE-1-04_evidence.md`:
- Commands + key outputs
- Manual checks:
  - Toggle visible only on demo route
  - Switching modes persists across refresh
  - Immersive mode collapses header/sidebar and changes content padding/typography

## Output in final response (no extra suggestions)
- Summary
- Commands
- Evidence path
