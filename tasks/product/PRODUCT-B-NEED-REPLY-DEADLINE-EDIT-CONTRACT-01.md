# PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01

Task ID: `PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01`

Story Shape Classification:
- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Freeze product/backend contract for `TC-B-013` main-screen `NeedReply` and deadline edits.

## Explicit Non-Closure

Do not:
- modify backend code
- modify pytest automation handlers
- modify frontend UI
- modify skeleton data
- implement task update/cancel behavior

## Remaining Follow-Up Task IDs

- `BE-B-NEED-REPLY-DEADLINE-EDIT-RULE-01`
- `B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01`

## Allowed Files

- `tasks/product/PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01.md`
- `docs/product/PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01.md`
- `artifacts/PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01/**`

## Verification Commands

```bash
test -f tasks/product/PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01.md
test -f docs/product/PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01.md
rg -n "NeedReply|Deadline|DOCUMENT_REPLY_TASK_UPDATE_REQUIRED|DOCUMENT_REPLY_TASK_CANCELLED|deferred" docs/product/PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01.md
./scripts/task_validate.sh PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01
```

## Evidence Path

- `artifacts/PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01/results.jsonl`
- `artifacts/PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01/summary.md`
- `artifacts/PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01/git/diff.patch`
