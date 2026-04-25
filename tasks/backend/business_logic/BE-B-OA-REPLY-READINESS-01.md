# BE-B-OA-REPLY-READINESS-01

Task ID: `BE-B-OA-REPLY-READINESS-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Verify and minimally fix OA reply path needed by `TC-B-006`, `TC-B-007`, and `TC-B-008`.

This task closes only:
- same-case `ReplyTo` enforcement
- reply-to-template enforcement
- reply document creation
- task auto write-off
- status restore when template config provides it

## Explicit Non-Closure

Do not:
- implement pytest automation handlers
- implement main-screen NeedReply/Deadline edit behavior
- implement OA fee/bill/payment/commission behavior
- modify frontend or skeleton data

## Remaining Follow-Up Task IDs

- `BE-B-OA-FINANCE-READINESS-01`
- `PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01`

## Allowed Files

- `tasks/backend/business_logic/BE-B-OA-REPLY-READINESS-01.md`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_b2_reply_chain.py`
- `artifacts/BE-B-OA-REPLY-READINESS-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/documents/service.py tests/test_b2_reply_chain.py
python3 -m ruff format app/modules/documents/service.py tests/test_b2_reply_chain.py
python3 -m ruff check app/modules/documents/service.py tests/test_b2_reply_chain.py
pytest tests/test_b2_reply_chain.py -q
./scripts/task_validate.sh BE-B-OA-REPLY-READINESS-01
```

## Evidence Path

- `artifacts/BE-B-OA-REPLY-READINESS-01/results.jsonl`
- `artifacts/BE-B-OA-REPLY-READINESS-01/summary.md`
- `artifacts/BE-B-OA-REPLY-READINESS-01/git/diff.patch`
