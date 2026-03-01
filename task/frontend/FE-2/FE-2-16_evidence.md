# FE-2-16 Evidence Log

## Commands Executed

### Lint + TypeCheck + Build
```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend
npm run lint && npm run typecheck && npm run build
```
**Result:** ✅ All passed (2.87s build)
- Updated chunks:
  - `fees-DAyP2I9T.js` (1.12 kB, was 0.97 kB)
  - `FeeDraftDetail-Buhv4SNK.js` (12.47 kB, was 10.51 kB)
  - `FeeDraftDetail-DBXgLvuB.css` (1.24 kB, was 1.10 kB)

## Files Modified

| File | Action |
|------|--------|
| `src/api/fees.ts` | Modified - added lockFeeDraft, unlockFeeDraft |
| `src/modules/fees/components/FeeDraftItemsTable.vue` | Modified - added readonly prop |
| `src/modules/fees/pages/FeeDraftDetail.vue` | Modified - lock/unlock UI |

## Manual Smoke Steps

### 1. Open Unlocked Draft
- Navigate to `/fees/drafts/{id}` (OPEN status)
- **Expected:**
  - "Lock" button visible
  - Items table shows add/edit/delete actions

### 2. Lock Draft
- Click "🔒 Lock" button
- Confirm in dialog
- **Expected:**
  - Status 200 on `POST /fees/drafts/{id}/lock`
  - Status changes to LOCKED
  - 🔒 LOCKED badge appears
  - Items table becomes read-only (no add/edit/delete)
  - Locked notice banner appears

### 3. Unlock Draft
- Click "🔓 Unlock" button
- Confirm in dialog
- **Expected:**
  - Status 200 on `POST /fees/drafts/{id}/unlock`
  - Status changes to OPEN
  - Edit actions re-enabled

### 4. 409 Conflict Handling
- Open draft in two tabs
- Lock in tab 1
- Try to lock/unlock in tab 2
- **Expected:**
  - 409 error banner with requestId
  - Toast: "Conflict: This draft may have been modified. Please refresh."

### 5. Refresh After Lock
- Click Refresh button
- **Expected:** UI reflects current lock state

## API Assumptions

| Endpoint | Method | Response |
|----------|--------|----------|
| `/fees/drafts/{id}/lock` | POST | `FeeDraftDetail` (200) |
| `/fees/drafts/{id}/unlock` | POST | `FeeDraftDetail` (200) |
| Error 409 | — | `{ error: { code, message, requestId } }` |
