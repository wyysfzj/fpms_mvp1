# FE-2-04 Evidence Log

## Date
2026-02-03

## Commands Executed

### Quality Gates
```bash
$ npm run lint
# Output: eslint . --max-warnings 0 (PASSED, 0 warnings)

$ npm run typecheck  
# Output: vue-tsc --noEmit (PASSED, no errors)

$ npm run build
# Output: vite build - ✓ 1551 modules transformed, built in 2.53s (PASSED)
```

## Files Modified/Created
- `src/api/cases.types.ts` - Extended Case type, added CaseUpdatePayload
- `src/api/cases.ts` - Added getCase(), updateCase() functions
- `src/modules/cases/pages/CaseDetail.vue` - Full implementation
- `src/modules/cases/pages/CaseEdit.vue` - New file
- `src/router/index.ts` - Added `/cases/:id/edit` route
- `src/styles/layout.css` - Added case detail CSS classes

## Manual Smoke Test Steps

### 1. Navigate to `/cases/:id`
- Start dev server: `npm run dev`
- Login with valid credentials
- Navigate to `/cases/1` (or any valid case ID)
- **Expected:** Loading skeleton → Case header card with case_no (mono font), client name, dates, title, status tag
- **Expected:** Tabs visible: Overview, Claims, Official Docs, Fees, Billing, Tasks
- **Expected:** 2-column layout (main panel + side panel)

### 2. Toggle Focus Mode
- Click Focus Mode toggle button (top-right corner)
- **Expected after toggle ON:**
  - Sidebar/header collapse
  - Content becomes single column
  - Side panel is hidden
  - Tab underline is removed
- Toggle OFF → verify 2-column layout restores

### 3. Edit Case
- Click "Edit Case" button → navigate to `/cases/:id/edit`
- Modify title field
- Click "Save Changes"
- **Expected:** Success message, redirect to detail page with updated title

## API Assumptions
- Backend `GET /cases/{id}` returns Case object with fields: id, case_no, title, client_id, client_name, status, filing_date, app_date, inventors, notes, created_at, updated_at
- Backend `PUT /cases/{id}` accepts CaseUpdatePayload and returns updated Case
- Backend returns 422 with validation details in standard envelope format for invalid input
