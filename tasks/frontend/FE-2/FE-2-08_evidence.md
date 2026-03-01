# FE-2-08 Evidence Log

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
# Output: vite build - ✓ 1559 modules transformed, built in 2.55s (PASSED)
```

## Files Modified
- `src/api/tasks.ts` - Added closeTask(), reopenTask(), cancelTask() functions
- `src/modules/tasks/pages/TaskList.vue` - Added Actions column with dropdown, confirmation dialogs, 409 handling

## Manual Smoke Test Steps

### 1. Open Task List
- Navigate to `/tasks`
- **Expected:** Table shows with Actions column (⋮ button)

### 2. Close Task
- Click Actions (⋮) on an open task
- Click "Close"
- **Expected:** 
  - Confirmation dialog appears
  - On confirm (200): Success message, list refreshes, task shows "closed" status

### 3. Reopen Task
- Click Actions (⋮) on a closed task
- Click "Reopen"
- **Expected:** 
  - Confirmation dialog
  - On confirm (200): Success message, list refreshes

### 4. Cancel Task
- Click Actions (⋮) on any task
- Click "Cancel" (appears with warning style)
- **Expected:** 
  - Warning confirmation dialog
  - On confirm (200): Success message, task shows "cancelled" status

### 5. Conflict Error (409)
- Try to transition a task to an invalid state
- **Expected (409):**
  - Error banner displays
  - Toast shows "Cannot [action] task: [message] (Request ID: xxx)"

## API Assumptions
- Backend `POST /tasks/{id}/close` returns updated Task
- Backend `POST /tasks/{id}/reopen` returns updated Task
- Backend `POST /tasks/{id}/cancel` returns updated Task
- Returns 409/400 with error message for invalid transitions
