# FE-3 QA Evidence

## Executed Task
- `tasks/frontend/FE-3/FE-3_QA_AUDIT_AND_FIX_PROMPT.md`

## Step 0: Baseline Gates

### Commands
```bash
cd frontend
npm install
npm run lint
npm run typecheck
npm run build
```

### Key Outputs
- `npm install`
  - `up to date, audited 260 packages in 2s`
- `npm run lint`
  - `eslint . --max-warnings 0` (PASS)
- `npm run typecheck`
  - `vue-tsc --noEmit` (PASS)
- `npm run build`
  - `vite build`
  - `✓ built in 3.26s` (PASS)

## Step 1: FE-3 Artifact Audit

### Commands
```bash
ls -la task/frontend/FE-3
sed -n '1,260p' docs/frontend_smoke_flows.md
for f in task/frontend/FE-3/FE-3-0*_evidence.md; do
  rg -n "Commands Executed|Outputs \(Key Lines\)|Manual Verification Steps|Results|Smoke" "$f"
done
```

### Key Outputs
- `docs/frontend_smoke_flows.md` exists.
- Evidence logs exist:
  - `task/frontend/FE-3/FE-3-01_evidence.md`
  - `task/frontend/FE-3/FE-3-02_evidence.md`
  - `task/frontend/FE-3/FE-3-03_evidence.md`
  - `task/frontend/FE-3/FE-3-04_evidence.md`
  - `task/frontend/FE-3/FE-3-05_evidence.md`
  - `task/frontend/FE-3/FE-3-06_evidence.md`
  - `task/frontend/FE-3/FE-3-07_evidence.md`
- All FE-3 evidence files contain command/output/manual result sections (headings confirmed by grep).

## Step 2: Smoke Flow Verification (Static)

### Commands
```bash
sed -n '1,320p' frontend/src/router/index.ts
find frontend/src/modules -type f -path '*/pages/*.vue' | sort
rg -n "New Client|Create Case|Quick Edit|Create Task|Upload File|Download|New Rate|Create Draft|Add Item|Lock|Unlock|Create Bill|Print Bill|Record Payment|Create Offset|Upload Template|Add Parameter|Add Letterhead" frontend/src/modules frontend/src/components --glob '*.vue'
rg -n "from './http'" frontend/src/api/*.ts
rg -n "http\.(get|post|put|delete)" frontend/src/api/*.ts
curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1
```

### Key Outputs
- Router has FE-3 module routes for clients/cases/tasks/documents/fees/billing/system.
- Module pages/components and expected action labels are present.
- API access is centralized through `frontend/src/api/http.ts`.
- Backend availability probe returned `000` (backend not running at audit time).

## Step 3: UI Style Compliance Checks

### Commands
```bash
sed -n '1,260p' frontend/src/styles/variables.css
sed -n '1,260p' reference/fpms.css
sed -n '1,320p' frontend/src/styles/layout.css
rg -n -- "--color-primary|--color-success|--color-danger|--color-bg-body|--color-bg-panel|--color-bg-sidebar|--font-main|--font-read|--sidebar-width|--header-height|--radius-base|--shadow-card|--border-panel" frontend/src/styles/variables.css reference/fpms.css
```

### Key Outputs
- `frontend/src/styles/variables.css` token values match `reference/fpms.css` token block values for `:root` and `body.mode-immersive`.
- Verified in CSS:
  - Work mode uses `--sidebar-width: 240px`, `--header-height: 60px`, `.content-scroll { padding: 30px; }`.
  - Immersive mode uses `--sidebar-width: 0px`, `--header-height: 0px`, `.content-scroll { padding: 40px 15% 0 15%; }`.
  - `.case-content-grid` collapses to single-column in immersive mode and `.case-side-panel` / `.focus-reading-aside` are hidden.

## Step 4: Defect Fix Pass (Applied)

### Files Changed
- `frontend/src/api/clients.ts`
- `frontend/src/api/cases.ts`
- `frontend/src/api/documents.ts`
- `frontend/src/api/tasks.ts`
- `frontend/src/api/clients.types.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/api/tasks.types.ts`
- `frontend/src/api/system.ts`
- `frontend/src/api/system.types.ts`
- `frontend/src/modules/clients/pages/ClientForm.vue`
- `frontend/src/modules/clients/pages/ClientList.vue`
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `frontend/src/modules/cases/components/LimitedEditDialog.vue`
- `frontend/src/modules/documents/pages/DocumentList.vue`
- `frontend/src/modules/documents/pages/DocumentDetail.vue`
- `frontend/src/modules/documents/pages/DocumentEdit.vue`
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `frontend/src/modules/documents/components/AttachmentList.vue`
- `frontend/src/modules/tasks/pages/TaskList.vue`
- `frontend/src/modules/tasks/pages/TodayReminders.vue`
- `frontend/src/modules/billing/pages/BillList.vue`
- `frontend/src/styles/layout.css`

### Applied Fixes (Summary)
- Removed numeric route-ID coercion for case/document detail/edit and client edit paths.
- Fixed client list `View` action route to avoid non-existent path.
- Added document list `View` action and bills list `New Bill` CTA.
- Fixed task action API calls to send `{}` payload for action endpoints.
- Fixed today reminders API handling to consume paginated response (`items`).
- Mapped document attachment backend fields (`file_name`, `uploaded_at`) to UI fields.
- Mapped system params backend keys/payload (`param_key`, `param_value`) to UI contract.
- Corrected immersive content padding to `40px 15% 0 15%`.

## Step 4: Post-Fix Gates

### Commands
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

### Key Outputs
- `npm run lint`
  - `eslint . --max-warnings 0` (PASS)
- `npm run typecheck`
  - `vue-tsc --noEmit` (PASS)
- `npm run build`
  - `vite build`
  - `✓ built in 3.18s` (PASS)

## Runtime Smoke Verification
- Not executed in this QA run because backend was not available at `http://localhost:8000/api/v1` during audit (`curl` returned `000`).
- Runtime outcomes were not fabricated.

## Runtime Re-Run (Post Backend Availability)

### Executed Task
- `tasks/frontend/FE-3/FE-3_RUNTIME_SMOKE_AND_CONTRACT_FIX_PROMPT.md`

### Connectivity + Login Commands
```bash
curl -i "http://localhost:8000/api/v1/clients?page=1&page_size=1"
curl -s http://localhost:8000/openapi.json | head
curl -s http://localhost:8000/openapi.json | jq -r '.paths | keys[]' | rg -i "auth|login|token"
curl -sS -o /tmp/fpms_login.json -w "%{http_code}" \
  -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Runtime Smoke Command
```bash
bash /tmp/fe3_runtime_smoke.sh
```

### Runtime Summary
- Backend probe: `401` with request ID (reachable)
- Login: `200`
- Total runtime calls: `56`
- Successful `2xx`: `41`
- Non-2xx: `15`

### Key Runtime Blockers Observed
- `POST /documents/{id}/attachments` -> `500`
- `GET /bills/{id}/print` -> `409` (template config)
- `POST /offsets` -> `404 PAYMENT_LINE_NOT_FOUND`

### Post-fix Gates
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

- `lint`: PASS
- `typecheck`: PASS
- `build`: PASS

### Related Runtime Artifacts
- `task/frontend/FE-3/FE-3_RUNTIME_SMOKE_REPORT.md`
- `task/frontend/FE-3/FE-3_RUNTIME_SMOKE_EVIDENCE.md`
- `/tmp/fe3_runtime_results.jsonl`
