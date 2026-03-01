# AI‑EOS PROMPT — FE‑0‑00
## Title
FE‑0‑00: Fix Vite entry + add lint/typecheck/build quality gates (minimal, stable)

## Context
You are working in the FPMS MVP1 frontend repository (Vue 3 + TypeScript + Vite + Pinia + Element Plus).
Current baseline issues:
- Vite build requires `index.html` at repo root.
- There are no `lint` / `typecheck` scripts yet, so we cannot produce AI‑EOS evidence logs per task.

## Objective
Make the project buildable and enforceable with quality gates:
1) Add missing Vite entry (`index.html`) so `npm run dev` and `npm run build` work.
2) Add TypeScript/Vite typing baseline (`src/vite-env.d.ts`) and ensure `import.meta.env` types resolve.
3) Add `lint` and `typecheck` scripts and minimal ESLint config suitable for Vue3 + TS.
4) Provide an Evidence Log with exact commands and key outputs.

## Non‑Goals (hard constraints)
- Do NOT implement business features (clients/cases/tasks/etc).
- Do NOT redesign UI/layout.
- Do NOT add heavy dependencies (no full formatting stack unless absolutely required). Keep to the minimal lint/typecheck gates.

## File Allowlist (ONLY modify/add these)
- `index.html` (add)
- `package.json`
- `tsconfig.json`
- `vite.config.ts` (only if required)
- `src/vite-env.d.ts` (add)
- ESLint config files (choose ONE approach):
  - `.eslintrc.cjs` (+ optional `.eslintignore`) OR
  - `eslint.config.js` (flat config)
- Evidence Log output:
  - `task/frontend/FE-0/FE-0-00_evidence.md` (add; create directories if missing)

If you believe additional files are required, STOP and output a *new smallest atomic fix task* with its own allowlist. Do not proceed.

## Implementation Requirements
1) Create `index.html` with:
   - `<div id="app"></div>`
   - `<script type="module" src="/src/main.ts"></script>`
   - Minimal meta tags; keep it clean.

2) Add `src/vite-env.d.ts`:
   - `/// <reference types="vite/client" />`
   - Ensure `.vue` SFC module types are available for TS tooling.

3) Update `tsconfig.json`:
   - Ensure TS can resolve Vite env typings (either via `vite-env.d.ts` or `compilerOptions.types` includes `vite/client`).
   - Keep `strict: true`.

4) Add `typecheck` script:
   - Add `vue-tsc` as devDependency.
   - Script should be `vue-tsc --noEmit`.

5) Add `lint` script:
   - Add ESLint + Vue + TypeScript lint stack (minimal recommended set).
   - Script should lint `.ts` and `.vue` and fail on warnings (`--max-warnings 0`).
   - Avoid stylistic rules that cause churn; focus on correctness/bugs.

6) Ensure the repo passes:
   - `npm run lint`
   - `npm run typecheck`
   - `npm run build`

## Evidence Log (mandatory)
Write `task/frontend/FE-0/FE-0-00_evidence.md` with:
- Commands executed (copy/paste exact)
- Key outputs (success lines; if failure, include the error and how you fixed it)
- Final confirmation that lint/typecheck/build all pass

## Execution Steps (do them in order)
1) Install deps: `npm install`
2) Implement changes per requirements
3) Run gates:
   - `npm run lint`
   - `npm run typecheck`
   - `npm run build`
4) Write Evidence Log

## Output in your final response (no extra suggestions)
- A brief change summary (bullet list)
- The exact commands you ran
- The path to the Evidence Log
