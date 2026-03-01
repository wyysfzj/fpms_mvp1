# FE-3-06 Evidence Log

## Task
- ID: FE-3-06
- Title: Polish: Focus Mode sweep for long-form pages (Case/Document) + route opt-in audit

## File Allowlist Respected
- ✅ Yes
- Files changed:
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `frontend/src/modules/documents/pages/DocumentDetail.vue`
  - `frontend/src/styles/layout.css`
  - `task/frontend/FE-3/FE-3-06_evidence.md`
- Files audited with no code change required:
  - `frontend/src/router/index.ts` (both `case_detail` and `document_detail` already have `meta.supportsFocusMode = true`)

## Commands Executed
```bash
# Quality gates
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run build

# Focus mode UI smoke
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000
cd frontend && npm run dev
cd frontend && NODE_PATH=./node_modules node /tmp/fe3_06_focus_smoke.js > /tmp/fe3_06_focus_results.json
```

## Outputs (Key Lines)
- `npm run lint`: ✅ passed (`eslint . --max-warnings 0`)
- `npm run typecheck`: ✅ passed (`vue-tsc --noEmit`)
- `npm run build`: ✅ passed (`vite build` complete)
- Focus smoke output: `/tmp/fe3_06_focus_results.json`

## Manual Verification Steps + Results

### 1) Open Case detail long-form tab; toggle immersive mode
- Route: `/cases/1`, tab: `Claims`, action: click `Enter Focus Mode`.
- Result: ✅ passed.
- Observed API status: `GET /api/v1/cases/1 -> 200`.

### 2) Confirm single-column reading layout + typography changes
- Checked in immersive mode:
  - `body.mode-immersive` present
  - `.focus-reading-main` max-width = `760px`
  - reading font on long-form content uses `"Noto Serif SC", "Songti SC", serif`
  - reading font size in immersive = `18px`, line-height = `36px`
- Result: ✅ passed for Case detail (Claims).

### 3) Confirm side panel is hidden
- Case detail Overview:
  - `.case-side-panel` display = `none` in immersive mode.
- Result: ✅ passed.

### 4) Repeat for Document detail
- Route: `/documents/1` while immersive remains enabled.
- Verified:
  - `.case-side-panel` display = `none`
  - `.focus-reading-main` max-width = `760px`
  - reading typography active on document content (`font-read`, 18px / 36px)
- Result: ✅ passed.
- Observed API statuses:
  - `GET /api/v1/documents/1 -> 200`
  - `GET /api/v1/documents/1/attachments -> 200`

### 5) Refresh and confirm mode persistence
- Refreshed `/cases/1` after enabling immersive mode.
- Verified:
  - `body.mode-immersive` still present
  - mode toggle text shows `Exit Focus Mode`
- Result: ✅ passed.

## Focus Smoke Summary
From `/tmp/fe3_06_focus_results.json`:
- `case_claims_immersive_layout`: success=true
- `case_overview_side_panel_hidden`: success=true
- `mode_persistence_after_refresh`: success=true
- `document_immersive_layout`: success=true

## Mismatches / Handling
- Observed background request from case detail billing component:
  - `GET /api/v1/cases/1/receipts -> 404`
- Impact: no impact on Focus Mode validation scope (layout and immersive behavior unaffected).
- Action: documented only; no out-of-scope feature/API change applied.
