# FE-2-03 Evidence Log: Cases List + Create

**Task**: Implement Cases list page (`/cases`) and Case create page (`/cases/new`)  
**Date**: 2026-02-03

---

## Files Modified/Created

| File | Action |
|------|--------|
| `src/api/cases.types.ts` | NEW |
| `src/api/cases.ts` | NEW |
| `src/modules/cases/pages/CaseList.vue` | MODIFIED (replaced placeholder) |
| `src/modules/cases/pages/CaseCreate.vue` | NEW |
| `src/router/index.ts` | MODIFIED (added `/cases/new` route) |

---

## Quality Gate Results

### npm run lint
```
> fpms-spa@0.1.0 lint
> eslint . --max-warnings 0

(no output = pass)
```
**Result**: ✅ PASS

### npm run typecheck
```
> fpms-spa@0.1.0 typecheck
> vue-tsc --noEmit

(no output = pass)
```
**Result**: ✅ PASS

### npm run build
```
> fpms-spa@0.1.0 build
> vite build

vite v5.4.21 building for production...
✓ 1548 modules transformed.
dist/index.html                             0.64 kB │ gzip:   0.41 kB
dist/assets/CaseCreate-BZlDGXx2.css         0.27 kB │ gzip:   0.17 kB
dist/assets/CaseList-Cu8KndP7.js            3.23 kB │ gzip:   1.47 kB
dist/assets/CaseCreate-YmCcIC8b.js          3.50 kB │ gzip:   1.58 kB
...
✓ built in 2.53s
```
**Result**: ✅ PASS

---

## Manual Smoke Test Steps

### 1. Cases List Page
1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Login at `/login` with valid credentials
4. Navigate to `/cases`
5. **Expected**:
   - If cases exist: Table shows ID, Case No, Title, Client, Status, Updated columns
   - If no cases: Empty state with "No cases yet" message
   - "New Case" button visible in header
   - Request: `GET /api/v1/cases?page=1&page_size=20` returns 200

### 2. Case Create Page
1. Click "New Case" button or navigate to `/cases/new`
2. **Expected**:
   - Form with Case Number, Title, Client dropdown fields
   - Client dropdown populated with clients from API
3. Submit with empty Case Number
   - **Expected**: Client-side validation error "Case number is required"
4. Fill Case Number, leave Client empty
   - **Expected**: Validation error "Please select a client"
5. Fill all required fields and submit
   - **Expected**: `POST /api/v1/cases` → 201 (success) or 422 (validation)
   - On success: Redirects to `/cases` with success message

### 3. Error Handling
1. Stop backend, try to load `/cases`
   - **Expected**: Error banner with network error message
2. Submit form with backend down
   - **Expected**: Error banner shows with request ID if available

---

## API Assumptions

| Endpoint | Assumption | Verified |
|----------|------------|----------|
| `GET /cases` | Returns `{ items, page, page_size, total }` | Pending backend test |
| `POST /cases` | Accepts `{ case_no, title?, client_id }` | Pending backend test |
| `GET /clients` | Existing endpoint for client dropdown | ✅ Used existing implementation |

---

## Implementation Notes

1. **Client Selection**: Uses simple dropdown fetching first 100 clients. If more clients exist, a hint is shown. Search/autocomplete not implemented as backend lacks `search` param.

2. **Pattern Adherence**: Followed `ClientList.vue` and `ClientForm.vue` patterns exactly for consistency.

3. **Date Formatting**: Uses `dayjs` for date formatting (already a project dependency).
