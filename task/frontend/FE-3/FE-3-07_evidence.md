# FE-3-07 Evidence Log

## Task
- Executed: `tasks/frontend/FE-3/FE-3-07_AI-EOS_PROMPT.md`
- Title: Polish: MVP A11y + micro-UX sweep (dialogs, dropdowns, reduced motion, aria)

## Commands Executed + Key Outputs

1. `cd frontend && npm run lint`
- Result: `PASS`
- Key output: `eslint . --max-warnings 0` completed with exit code `0`.

2. `cd frontend && npm run typecheck`
- Result: `PASS`
- Key output: `vue-tsc --noEmit` completed with exit code `0`.

3. `cd frontend && npm run build`
- Result: `PASS`
- Key output: `vite build` completed with exit code `0`.

4. UI smoke runtime setup:
- `cd backend && uvicorn app.main:app --host localhost --port 8000`
- `cd frontend && npm run dev`

5. A11y/micro-UX smoke script:
- `APP_URL=http://localhost:5173 node /tmp/fe3_07_a11y_smoke.cjs > /tmp/fe3_07_a11y_results.json`
- Result: `PASS` for required checks.

## Manual Verification Steps + Results

Source of run details: `/tmp/fe3_07_a11y_results.json`

1. Open/close dialog and verify focus lifecycle
- Route: `/system/templates`
- Action: focus `Upload Template` button via keyboard, press `Enter` to open, press `Escape` to close.
- Result: `PASS`
  - `beforeOpenFocused: true`
  - `focusInsideDialog: true`
  - `focusReturned: true`

2. Trigger dropdown row action using keyboard only
- Route: `/clients`
- Action: focus row `Actions` trigger, open menu with keyboard, activate `View` via keyboard.
- Result: `PASS`
  - Menu opened via keyboard.
  - Route changed to client detail path (`/clients/<id>`), confirming action invocation.

3. Toggle immersive mode using keyboard and confirm `aria-pressed`
- Route: `/focus-demo`
- Action: focus mode toggle and press `Space`.
- Result: `PASS`
  - `ariaBefore: "false"`
  - `ariaAfter: "true"`

4. Reduced motion behavior
- Route: `/focus-demo` in browser context with `prefers-reduced-motion: reduce`
- Result: `PASS`
  - `prefersReducedMotion: true`
  - `toggleTransitionDuration: "0s"`
  - `bodyTransitionDuration: "0s"`

## API Statuses + Request IDs Observed

From smoke run summary:
- `POST /auth/login` -> `200` (requestId example: `623d26db-44fd-4d05-b6d5-fc2bd384a668`)
- `GET /templates?page=1&page_size=20` -> `200` (requestId: `2cd3cebd-65ec-4417-8c20-9f13c4283cef`)
- `GET /clients?page=1&page_size=20` -> `200` (requestId: `48f2c4b3-1b4e-44d0-a388-20815ab8804e`)

## Mismatches / Handling
- No out-of-scope mismatch required STOP for this task.
- One scripted smoke attempt initially failed due host/CORS mismatch (`127.0.0.1` origin). Re-ran with `localhost` and completed successfully.
