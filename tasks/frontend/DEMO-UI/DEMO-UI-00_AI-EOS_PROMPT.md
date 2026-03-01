# AI‑EOS PROMPT — DEMO‑UI‑00
## Title
DEMO‑UI‑00: 三套可切换主题（A/B/C）+ 演示控制条（body class 切换）对齐 `reference/patent_ui.html`

## Context
现状：登录后为“可运行的 MVP 功能壳”（路由 + MainLayout）。客户 Demo 期望对齐静态演示稿 `reference/patent_ui.html` 的核心卖点：
- 三套主题 A/B/C
- 演示控制条（可切换主题）
- 通过切换 `body` class 实现风格切换（不改路由体系）

## Objective (Closed-loop)
1) 新增 Demo UI 开关：`VITE_DEMO_UI=1` 时启用演示控制条与主题切换；不开启时不影响现有 UI。
2) 实现主题 A/B/C 的切换：通过切换 `document.body.classList` 的 `theme-a|theme-b|theme-c`（具体 class 名必须与 `reference/patent_ui.html` 对齐，禁止自行发明）。
3) 主题切换需持久化（localStorage），刷新后保持。
4) 主题 CSS 变量/规则来源必须直接来自 `reference/patent_ui.html`（复制/抽取），禁止凭空“设计配色”。
5) 不允许修改 `frontend/src/styles/variables.css` 中既有 token block 的 **数值**（必须保持与 `reference/fpms.css` 一致）。

## Non‑Goals (hard)
- 不重构路由/页面结构
- 不做 Dashboard 视觉重做（DEMO‑UI‑02 才做）
- 不更改后端调用
- 不引入重 UI 依赖

## File Allowlist (ONLY modify/add these)
- `frontend/.env.example` (update: add VITE_DEMO_UI说明)
- `frontend/src/main.ts` (import new demo theme css if needed; boot apply theme)
- `frontend/src/stores/ui.ts` (update: add theme state + persistence + body class apply)
- `frontend/src/layout/MainLayout.vue` (update: mount DemoToolbar gated by env)
- `frontend/src/components/demo/DemoToolbar.vue` (new)
- `frontend/src/styles/demo-themes.css` (new; holds theme A/B/C extracted from patent_ui)
- `frontend/src/styles/base.css` (update ONLY if required to ensure demo css loaded)
- Evidence:
  - `task/frontend/DEMO-UI/DEMO-UI-00_evidence.md`

If you believe more files are needed: STOP and output the smallest follow-up task.

## Implementation Steps
### 1) Extract theme definitions from `reference/patent_ui.html`
- Open `reference/patent_ui.html`
- Locate:
  - theme A/B/C css variables / rules
  - the exact body class names used for switching
  - the demo control bar structure (visual + interactions)
- Create `frontend/src/styles/demo-themes.css` and copy ONLY the needed theme overrides.
  - IMPORTANT: keep `frontend/src/styles/variables.css` base token values unchanged.
  - Theme overrides must live in `demo-themes.css` under selectors like `body.theme-a { ... }`.

### 2) Add demo UI enable flag
- In `.env.example`, add:
  - `VITE_DEMO_UI=1` (commented example)
- In code, treat env vars as strings; recommended:
  - `const DEMO_UI = import.meta.env.VITE_DEMO_UI === '1'`

### 3) Implement theme state + persistence
- Update `frontend/src/stores/ui.ts`:
  - state: `theme: 'a'|'b'|'c'` (or matching names from patent_ui)
  - localStorage key: `fpms_ui_theme`
  - actions: `setTheme(theme)`, `applyThemeToBody()`
  - ensure exactly one theme class is active at a time

### 4) DemoToolbar component
- Create `frontend/src/components/demo/DemoToolbar.vue`
  - Only render when `DEMO_UI` flag is true
  - Provide A/B/C buttons; active state visible
  - On click: `uiStore.setTheme('a'|'b'|'c')`
  - Styling: replicate patent_ui control bar look & spacing; no inline styles

### 5) Mount toolbar in MainLayout
- Update `frontend/src/layout/MainLayout.vue`:
  - render `<DemoToolbar />` near the root of layout
  - gate it behind `DEMO_UI` flag

### 6) Manual Verification
- With `VITE_DEMO_UI=1`:
  - login -> see demo toolbar
  - click A/B/C -> body class changes accordingly
  - refresh page -> theme persists
- With `VITE_DEMO_UI` unset:
  - toolbar not shown
  - UI behaves exactly as before

## Quality Gates (mandatory)
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

## Evidence Log (mandatory)
Write `task/frontend/DEMO-UI/DEMO-UI-00_evidence.md`:
- commands + key outputs
- screenshots (A/B/C)
- proof `variables.css` base token values unchanged (mention how you checked)
