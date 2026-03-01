# FE-2-07 Evidence Log

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
# Output: vite build - ✓ 1558 modules transformed, built in 2.57s (PASSED)
```

## Files Created/Modified
- `src/api/tasks.types.ts` - Added TaskCreatePayload type
- `src/api/tasks.ts` - Added createTask() function
- `src/modules/tasks/pages/TaskCreate.vue` - New task creation page
- `src/router/index.ts` - Added /tasks/new route

## Manual Smoke Test Steps

### 1. Navigate to `/tasks/new`
- Start dev server: `npm run dev`
- Login and navigate to `/tasks/new`
- **Expected:** Form displays with fields: Title, Description, Case ID, Priority, Due Date, Assigned To

### 2. Validate Required Fields
- Leave Title empty and try to submit
- **Expected:** "Title is required" validation error
- Leave Case ID empty or 0 and try to submit
- **Expected:** "Case ID is required" / "Please enter a valid case ID" validation error

### 3. Submit Valid Task
- Fill in:
  - Title: "Test Task"
  - Case ID: 1 (or valid case ID)
  - Optional: Priority, Due Date, Assigned To
- Click "Create Task"
- **Expected (200):** 
  - Success message "Task created successfully"
  - Redirect to `/tasks`

### 4. Handle 422 Validation Error
- Submit with invalid data that passes client validation
- **Expected (422):**
  - Field errors mapped to respective form fields
  - Error banner with requestId if available

### 5. Helper Link
- Click "Browse Cases" link under Case ID field
- **Expected:** Navigates to `/cases` list

## API Assumptions
- Backend `POST /tasks` accepts: { title, description?, case_id, priority?, due_date?, assigned_to? }
- Returns created Task object on success (201/200)
- Returns 422 with validation details for invalid input
