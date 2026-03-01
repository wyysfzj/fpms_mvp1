# FE-2-22 Evidence Log

## Date
2026-02-07

## Commands Executed

### Quality Gates
```bash
$ npm run lint
# Output: eslint . --max-warnings 0 (PASSED, 0 warnings)

$ npm run typecheck
# Output: vue-tsc --noEmit (PASSED, no errors)

$ npm run build
# Output: vite build - built in 3.00s (PASSED)
# dist/assets/TemplateList-BtVvBjdi.js 6.59 kB
```

## Files Created/Modified
- `src/api/system.types.ts` - New: TemplateListItem, TemplateDetail, TemplateListParams, TemplateUploadPayload, SystemParamListItem, SystemParamUpsertPayload, LetterheadListItem, LetterheadCreatePayload
- `src/api/system.ts` - New: System API client with templates, params, letterheads functions
- `src/modules/system/pages/TemplateList.vue` - New: Templates list page with upload dialog
- `src/router/index.ts` - Added: /system/templates route

## Manual Smoke Test Steps

### 1. Navigate to `/system/templates`
- Start dev server: `npm run dev`
- Login and navigate to `/system/templates`
- **Expected:**
  - Templates table with columns: Code, Name, Type, Description, Updated, Actions
  - "Upload Template" button in header

### 2. Empty State
- If no templates
- **Expected:** Empty state with upload button

### 3. Upload Template
- Click "Upload Template" button
- Fill in dialog:
  - Code (required): e.g., "BILL_TEMPLATE_1"
  - Name (required): e.g., "Standard Bill"
  - Description (optional)
  - Select file (.docx, .xlsx, or .html)
- Click "Upload"
- **Expected (201):**
  - Success message
  - Dialog closes
  - Template appears in list

### 4. Delete Template
- Click "Delete" on a template row
- Confirm in dialog
- **Expected (204):**
  - Success message
  - Template removed from list

### 5. Validation Errors (422)
- Submit upload with missing code
- **Expected:** "Code is required" error

## API Assumptions
- `GET /templates` returns paginated list: { items, page, page_size, total }
- Template has: id, code, name, file_type, description, created_at, updated_at
- `POST /templates` accepts multipart/form-data with file
- `DELETE /templates/{id}` deletes template
