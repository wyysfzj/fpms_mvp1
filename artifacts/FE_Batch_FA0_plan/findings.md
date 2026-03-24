# Batch FA0 — Findings Log

> Bugs, discoveries, and deviations found during execution.

---

## Backend Health Check (Task #2) — backend-agent

**Date**: 2026-02-26
**Status**: ALL ENDPOINTS OPERATIONAL

### Server Health
- `GET /healthz` → **200 OK** (`{"status":"ok"}`)
- Server already running at http://localhost:8000 (no startup needed)

### Auth Login
- `POST /api/v1/auth/login` (admin/admin123) → **200 OK** — token obtained ✓

### Endpoint Availability

| Endpoint | HTTP Status | Notes |
|----------|-------------|-------|
| `GET /api/v1/cases` | **200** | Returns paginated list with case data |
| `GET /api/v1/documents` | **200** | UP |
| `GET /api/v1/tasks` | **200** | UP |
| `GET /api/v1/fees/drafts` | **200** | UP |
| `GET /api/v1/bills` | **200** | Returns `{"items":[],"page":1,"page_size":20,"total":0}` |
| `GET /api/v1/clients` | **200** | UP |
| `GET /api/v1/payments` | **200** | UP |

### Important Finding: Billing Route Path
- The billing router is mounted **without a prefix** in `router.py` (line 26)
- Correct path is `/api/v1/bills` (NOT `/api/v1/billing/bills`)
- Frontend code referencing `/billing/bills` will get 404
- Same applies to payments: correct path is `/api/v1/payments`

### Summary
- **7/7 key endpoints**: UP and responding correctly
- **Auth**: Working — admin/admin123 credentials valid
- **Data**: Cases and clients have seed data; bills/payments are empty (expected)

---

## Frontend Quality Gate Results (Task #3) — frontend-agent

**Date**: 2026-02-26
**Status**: ALL GATES PASSED ✅

### 1. Dependencies Install
- **Command**: `npm install`
- **Result**: `up to date, audited 258 packages in 5s`
- **Exit Code**: 0
- **Notes**: 6 vulnerabilities (3 moderate, 3 high) — audit-level, not blocking
- **Verdict**: ✅ PASS

### 2. ESLint (`npm run lint`)
- **Command**: `eslint . --max-warnings 0`
- **Exit Code**: 0
- **Errors**: 0
- **Warnings**: 0
- **Verdict**: ✅ PASS

### 3. TypeScript Check (`npm run typecheck`)
- **Command**: `vue-tsc --noEmit`
- **Exit Code**: 0
- **Errors**: 0
- **Verdict**: ✅ PASS

### 4. Production Build (`npm run build`)
- **Command**: `vite build`
- **Exit Code**: 0
- **Build Time**: 3.11s
- **Modules Transformed**: 1,668
- **Output**: 65 assets in `dist/`
- **Warning**: Main chunk `index-Crevr7Qp.js` is 1,071.96 kB (>500 kB). Vite recommends code-splitting. Pre-existing, non-blocking.
- **Verdict**: ✅ PASS

### 5. Dev Server
- **Command**: `npx vite --port 5173`
- **Startup Time**: 176ms
- **curl test**: `http://localhost:5173` → 200 OK
- **Verdict**: ✅ PASS (DEV SERVER: UP)

### Summary

| Gate | Status | Exit Code |
|------|--------|-----------|
| npm install | ✅ PASS | 0 |
| ESLint | ✅ PASS | 0 |
| vue-tsc --noEmit | ✅ PASS | 0 |
| vite build | ✅ PASS | 0 |
| Dev Server | ✅ UP | — |

**Non-blocking observations:**
- 6 npm audit vulnerabilities (3 moderate, 3 high) — dependency-level, not source code
- Large main chunk (1,072 kB) — pre-existing, consider code-splitting in future
- No source files were modified

---

## Smoke Test Results (Task #4) — test-agent

**Date**: 2026-02-26
**Status**: ALL CHECKS PASSED ✅

### Infrastructure Status

| Component | Status | Notes |
|-----------|--------|-------|
| Backend Server | ✅ UP | `GET /healthz` → 200 `{"status":"ok"}` |
| Frontend Dev Server | ⚠️ DOWN | Not running at time of test (build artifacts exist) |
| Frontend Build (`dist/`) | ✅ EXISTS | 65 assets, built 2026-02-26 |

### API Smoke Test — 10-Point Checklist

| # | Frontend Page | API Endpoint | HTTP Status | Result |
|---|--------------|-------------|-------------|--------|
| 1 | /login | `POST /api/v1/auth/login` | 200 | ✅ PASS — token obtained |
| 2 | /dashboard | `GET /cases, /tasks, /documents, /fees/drafts` | 200 each | ✅ PASS |
| 3 | /cases | `GET /api/v1/cases` | 200 | ✅ PASS — paginated list |
| 3b | /cases/new | `POST /api/v1/cases` (empty body) | 422 | ✅ PASS — schema validates |
| 4 | /documents | `GET /api/v1/documents` | 200 | ✅ PASS |
| 5 | /tasks | `GET /api/v1/tasks` | 200 | ✅ PASS |
| 5b | /tasks/today | `GET /api/v1/tasks/today` | 200 | ✅ PASS |
| 6 | /fees/drafts | `GET /api/v1/fees/drafts` | 200 | ✅ PASS |
| 6b | /fees/rates | `GET /api/v1/fees/rates` | 200 | ✅ PASS |
| 7 | /billing/bills | `GET /api/v1/bills` | 200 | ✅ PASS — empty list (expected) |
| 7b | /billing/payments | `GET /api/v1/payments` | 200 | ✅ PASS — empty list (expected) |
| 8 | /clients | `GET /api/v1/clients` | 200 | ✅ PASS |
| 9 | /system/params | `GET /api/v1/system/params` | 200 | ✅ PASS |

**Result: 14/14 checks PASS**

### Important Finding: Billing Route Paths

The task spec listed billing endpoints as `/billing/bills` and `/billing/payments`, but the actual backend routes are:
- `/api/v1/bills` (NOT `/api/v1/billing/bills`)
- `/api/v1/payments` (NOT `/api/v1/billing/payments`)

The frontend API client (`frontend/src/api/billing.ts`) correctly uses `/bills` and `/payments`, so there is no frontend-backend mismatch. This is a documentation/spec discrepancy only.

### Backend Test Suite

- **Command**: `pytest -q --tb=short`
- **Result**: **141 passed** in 31.94s
- **Warnings**: 3 (deprecation warnings from passlib and Pydantic — non-blocking)
- **Failures**: 0

### Frontend Tests

- **No frontend test files found** — no `*.test.ts`, `*.spec.ts`, `tests/`, `__tests__/` directories exist.
- Frontend quality is verified via lint + typecheck + build gate only.

### Summary

- **Backend API**: All 14 endpoint checks pass. 141 unit tests pass.
- **Frontend Build**: Exists and valid (65 assets, built today).
- **Frontend Dev Server**: Not running at test time (non-blocking — build verified).
- **No source files were modified** during testing.
