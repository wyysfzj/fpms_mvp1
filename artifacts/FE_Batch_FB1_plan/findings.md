# Batch FB1 — Findings Log

> Bugs, discoveries, and deviations found during execution.

---

## Bug #1 — `canReopen()` missing CANCELLED status (MEDIUM)

**File**: `TaskDetail.vue:214-217`
**Found by**: reviewer-agent (T5)

`canReopen()` only checks for 'closed', 'completed', 'done' but does NOT include 'cancelled'. Per spec, CANCELLED tasks should show the reopen button. Users cannot reopen cancelled tasks from the detail page.

**Fix**: Add `|| s === 'cancelled' || s === 'canceled'` to the condition.

---

## Bug #2 — `canCancel()` too permissive for DONE status (LOW-MEDIUM)

**File**: `TaskDetail.vue:219-222`
**Found by**: reviewer-agent (T5)

`canCancel()` returns true for DONE tasks. Per spec, DONE should only show [重新打开]. The cancel button should not appear for completed tasks.

**Fix**: Add exclusions for 'done', 'completed', 'closed' statuses.

---

## Note #1 — `TaskLog.created_by` not in type (LOW)

**Found by**: test-agent (T4), confirmed by reviewer-agent (T5)

Backend `TaskLogOut` schema does not expose `created_by` from AuditMixin. Frontend `TaskLog` type doesn't include it either. Timeline omits actor display. Non-blocking — backend enhancement needed first.
