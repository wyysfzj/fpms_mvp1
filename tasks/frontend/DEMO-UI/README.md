# DEMO-UI — AI‑EOS Prompts Pack (for Codex / Claude / Gemini)

This pack converts your 3 customer-demo goals into **four** minimal atomic tasks:

- **DEMO‑UI‑00** — Theme A/B/C + Demo Toolbar (body class switching) aligned to `reference/patent_ui.html`
- **DEMO‑UI‑01** — 全站核心中文化 + 导航命名对齐 `patent_ui.html`
- **DEMO‑UI‑02** — Dashboard 工作台结构对齐 `patent_ui.html`（KPI + 待办表格 + 状态标签）
- **DEMO‑UI‑03** — 关系链 UX：客户 → 案件 → 文档 → 费用 → 账单（关系卡 + 可点击跳转 + 面包屑/来源标记）

> Why DEMO‑UI‑00 exists:
> `patent_ui.html` 的 Demo 核心是 **三套主题 A/B/C** + **演示控制条**，这是与当前 MVP “功能壳”观感差异最大的部分，所以必须作为单独最小任务闭环。

## Run Order
1) DEMO‑UI‑00
2) DEMO‑UI‑01
3) DEMO‑UI‑02
4) DEMO‑UI‑03

## Global Constraints (apply to every task)
- Keep backend usage unchanged; do not invent endpoints.
- Keep existing auth/RBAC behavior intact.
- **Do not modify the base token block values** in `frontend/src/styles/variables.css`.
  - Theme overrides MUST be implemented in separate CSS (e.g. `demo-themes.css`) under body theme classes.
- No inline styles in Vue templates; use class + token-driven CSS.
- Reference UI: `reference/patent_ui.html` (static demo) and `reference/case_detail.html`.
- Evidence must be written to `task/frontend/DEMO-UI/<task>_evidence.md`.

## Mandatory Gates (per task)
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

## Manual Verification (per task)
Each task prompt defines explicit manual checks. Capture screenshots + requestId where relevant.
