# FE-2-06 Evidence Log

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
# Output: vite build - ✓ 1555 modules transformed, built in 2.51s (PASSED)
```

## Files Created/Modified
- `src/api/tasks.types.ts` - New: Task interface and TaskListParams
- `src/api/tasks.ts` - New: getTasks() function
- `src/modules/tasks/pages/TaskList.vue` - Replaced stub with full implementation
- `src/styles/layout.css` - Added task list styles (priority colors, due date urgency)

## Manual Smoke Test Steps

### 1. Navigate to `/tasks`
- Start dev server: `npm run dev`
- Login and navigate to `/tasks`
- **Expected:** 
  - Loading skeleton appears
  - Table renders with columns: ID, Title, Case, Status, Priority, Due Date, Assigned, Updated

### 2. Verify Status Tags
- **Expected:** Status column shows colored tags:
  - Green: completed/done
  - Yellow: in_progress
  - Red: overdue/blocked
  - Blue: pending

### 3. Verify Due Date Urgency
- Tasks due within 3 days should show red text
- **Expected:** Urgent due dates highlighted with danger color

### 4. Pagination
- Change page size and navigate pages
- **Expected:** Table updates with new data

### 5. Error Handling
- If API fails, error banner shows with requestId

## API Assumptions
- Backend `GET /tasks` returns paginated response: `{ items, page, page_size, total }`
- Task object has: id, title, description, case_id, case_no, status, priority, due_date, assigned_to, created_at, updated_at
