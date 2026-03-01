# FE‑3 QA Audit & Defect Fix Prompt (for Codex / Gemini / Claude)

> Use this prompt in a coding agent that can read the repo, run shell commands, and edit files.

## Role
You are a **QA Auditor + Fixer** for FPMS MVP1 Frontend **after Phase FE‑3** completion.

Your job:
1) **Audit FE‑3 outputs**, especially smoke test results.
2) Produce a **QA review report** with a pass/fail matrix and defect list.
3) If defects exist, **implement fixes** (batched is allowed) while keeping changes minimal and style‑compliant.
4) Re-run gates and update evidence.

## Non‑Negotiable Constraints
- UI source of truth:
  - `reference/case_detail.html` (layout + immersive behaviors)
  - `fpms.css` (tokens spec; `src/styles/variables.css` variable block must match EXACTLY)
- Do NOT modify the token variable block values.
- Do NOT add heavy dependencies (no Cypress/Playwright, no UI libraries).
- Do NOT hardcode colors/spacing in Vue templates (no inline styles, no magic numbers).
- If you find an endpoint/contract mismatch, STOP and write a smallest fix proposal instead of guessing.

## Inputs (expected in repo)
- `docs/frontend_smoke_flows.md` (FE‑3‑01)
- `task/frontend/FE-3/FE-3-01_evidence.md` ... `FE-3-07_evidence.md` (or equivalent evidence logs)
- Frontend pages for modules: Clients/Cases/Tasks/Documents/Fees/Billing/System

## Required Outputs
Create/overwrite these files:
1) `task/frontend/FE-3/FE-3_QA_REVIEW_REPORT.md`
2) `task/frontend/FE-3/FE-3_QA_EVIDENCE.md`

The report must include:
- Executive summary
- FE‑3 artifact checklist (present/missing)
- Smoke flows pass/fail matrix
- Defects list with severity + reproduction steps + expected vs actual + root cause + fix status
- UI style compliance checks (tokens + immersive behaviors)
- Gate results (lint/typecheck/build)

## Step 0 — Environment & Gates (Baseline Evidence)
Run:
```bash
npm install
npm run lint
npm run typecheck
npm run build
```
Record the key output lines into `task/frontend/FE-3/FE-3_QA_EVIDENCE.md`.

If any gate fails:
- Treat as **Critical defect**.
- Fix it first (minimal changes).
- Re-run gates and record the final passing outputs.

## Step 1 — FE‑3 Artifact Audit
Check existence and completeness:
- `docs/frontend_smoke_flows.md`
- Evidence logs under `task/frontend/FE-3/`

For each evidence log:
- Verify it includes commands + outputs + manual steps + results.
- If missing content, record as a defect (“evidence incomplete”) and fix by updating the evidence log (do not fabricate results; re-run steps where possible).

## Step 2 — Smoke Flow Verification (Audit-first)
### 2.1 Build a Smoke Checklist
Parse `docs/frontend_smoke_flows.md` into a checklist of flows:
- Auth/session
- Clients
- Cases
- Tasks
- Documents (attachments upload/download)
- Fees (drafts/items/lock)
- Billing (bills create/print + payments/offsets + receipts)
- System/Templates

Create a “pass/fail” table in `FE-3_QA_REVIEW_REPORT.md`.

### 2.2 Verify Against the Actual UI Implementation (Static + Runtime)
Because full browser automation is not allowed, do both:

#### A) Static Verification (must do)
For each flow step:
- Verify routes exist in `src/router/index.ts`
- Verify referenced pages/components exist
- Verify key UI actions exist:
  - Search for button labels / action names in Vue templates
  - Confirm navigation paths are correct
- Verify API calls used by pages:
  - Confirm they go through the shared API client
  - Confirm endpoint paths match backend expectations
- If docs steps do not match UI (e.g., label changed), record a defect and update the docs for accuracy.

#### B) Runtime Verification (do if backend is available)
If the backend is running at `http://localhost:8000/api/v1`:
- Start frontend:
  ```bash
  npm run dev
  ```
- Manually execute each smoke flow in a browser and record:
  - success/failure
  - any 401/403/422/409 handling behavior
  - requestId visibility when present (from error UI)
- Update the pass/fail matrix accordingly.

If backend is NOT available:
- Record as a “Blocker: backend not running” and only complete static verification.
- Do NOT fabricate runtime outcomes.

## Step 3 — UI Style Compliance Checks (Strict)
### 3.1 Tokens block exactness
Compare `src/styles/variables.css` to the token block required by `fpms.css`.
- The `:root { ... }` block and `body.mode-immersive { ... }` block MUST match exactly (names + values).
- If mismatch exists, record as Critical defect and fix by restoring exact values.

### 3.2 Immersive mode behavior (must match reference)
Verify the following behaviors exist and work:
- Work Mode:
  - Sidebar width = 240px
  - Header height = 60px
  - Content padding = 30px
- Immersive Mode (`body.mode-immersive`):
  - Sidebar collapses (width -> 0)
  - Header collapses (height -> 0)
  - Content becomes paper-like layout (e.g. padding `40px 15% 0 15%`)
  - Two-column layouts become single-column
  - Side panels/timelines hide
- If any page breaks layout or remains two-column in immersive mode, record defect and fix.

## Step 4 — Defect Fix Pass (Batch Fix Allowed)
If defects are found:
- You MAY fix multiple defects in one pass (this bypasses strict “one task = one PR”).
- However you MUST:
  - Keep changes minimal and localized
  - Preserve tokens and style rules
  - Avoid new dependencies

Fix priority order:
1) Build/lint/typecheck failures
2) Broken smoke flows (cannot complete)
3) Wrong endpoint wiring / wrong pagination shape / missing requestId display
4) UI style regressions in immersive mode
5) A11y regressions (keyboard, aria-pressed, focus traps)

After implementing fixes:
- Re-run gates:
  ```bash
  npm run lint
  npm run typecheck
  npm run build
  ```
- If backend available, re-run the affected smoke flows manually.
- Update:
  - `docs/frontend_smoke_flows.md` if steps changed
  - `FE-3_QA_REVIEW_REPORT.md` defect statuses (Fixed / Not fixed / Blocked)

## Step 5 — Write Final QA Review Report
Write `task/frontend/FE-3/FE-3_QA_REVIEW_REPORT.md` with:

### A) Summary
- Overall status: PASS / PASS with minor issues / FAIL
- Gate status
- Backend availability

### B) Smoke Flow Matrix
| Flow | Status | Notes | Evidence |
|---|---|---|---|

### C) Defects
For each defect:
- ID: FE3-DEF-XXX
- Severity: Blocker/Critical/Major/Minor
- Module/Page:
- Steps to reproduce:
- Expected:
- Actual:
- requestId (if applicable):
- Root cause:
- Fix:
- Status: Fixed / Not fixed / Blocked

### D) UI Style Compliance
- Tokens exactness (pass/fail)
- Immersive behaviors (pass/fail per long-form page)

### E) Evidence
- Commands + key outputs
- Manual checks performed

## Final Response (what you tell the user)
Return:
- Where the QA report is located
- Where the QA evidence is located
- Short summary of key defects and what was fixed
