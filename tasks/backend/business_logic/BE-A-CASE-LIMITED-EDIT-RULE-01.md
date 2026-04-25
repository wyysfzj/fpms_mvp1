# BE-A-CASE-LIMITED-EDIT-RULE-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement the TC-A-010 backend limited-edit rule based on `PRODUCT-A-CASE-LIMITED-EDIT-CONTRACT-01`.

This task closes only:

1. Wire `POST /api/v1/cases/{case_id}/limited-edit` to `CaseUpdateLimited` and `update_case_limited`.
2. Support MVP whitelist fields: title fields, spec fields, and inventors.
3. Ensure blacklist fields submitted to limited-edit do not mutate case detail.
4. Return stable updated case detail.

## Explicit Non-Closure

Do not implement pytest automation, frontend UI, notes/remarks persistence, schema migration, task/fee generation, or unrelated case edit behavior.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-LIMITED-EDIT-P0-01
- BATCH-A-WAVE-CLOSE-AUDIT-01

## Allowed Files

- tasks/backend/business_logic/BE-A-CASE-LIMITED-EDIT-RULE-01.md
- backend/app/modules/cases/api.py
- backend/app/modules/cases/schemas.py
- backend/app/modules/cases/service.py
- backend/tests/test_case_limited_edit_rule.py
- artifacts/BE-A-CASE-LIMITED-EDIT-RULE-01/**

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/cases/api.py app/modules/cases/schemas.py app/modules/cases/service.py tests/test_case_limited_edit_rule.py
python3 -m ruff format app/modules/cases/api.py app/modules/cases/schemas.py app/modules/cases/service.py tests/test_case_limited_edit_rule.py
python3 -m ruff check app/modules/cases/api.py app/modules/cases/schemas.py app/modules/cases/service.py tests/test_case_limited_edit_rule.py
pytest tests/test_case_limited_edit_rule.py -q
```

## Evidence Path

- artifacts/BE-A-CASE-LIMITED-EDIT-RULE-01/results.jsonl
- artifacts/BE-A-CASE-LIMITED-EDIT-RULE-01/summary.md
- artifacts/BE-A-CASE-LIMITED-EDIT-RULE-01/git/diff.patch
