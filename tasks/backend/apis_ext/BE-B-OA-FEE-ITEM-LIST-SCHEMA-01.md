# BE-B-OA-FEE-ITEM-LIST-SCHEMA-01

Task ID: `BE-B-OA-FEE-ITEM-LIST-SCHEMA-01`

Story Shape Classification:
- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Fix the OA fee item list response schema so wizard-created `OA_FEE` fee items can be listed through `GET /api/v1/fees/drafts/{draft_id}/items`.

This task closes only:

1. Wizard-created fee items without `rate_id` serialize successfully.
2. Existing rate-driven fee item responses remain backward-compatible.
3. The list endpoint returns stable item fields required by `TC-B-009`.

## Explicit Non-Closure

Do not implement pytest automation handlers.
Do not modify fee generation logic.
Do not modify billing, payment, commission, documents, frontend, or skeleton data.

## Remaining Follow-Up Task IDs

- `BE-B-OA-BILL-PAYMENT-READINESS-01`
- `BE-B-OA-COMMISSION-READINESS-01`
- `B-AUTO-PY-B-OA-FEE-DRAFT-P1-01`

## Allowed Files

- `tasks/backend/apis_ext/BE-B-OA-FEE-ITEM-LIST-SCHEMA-01.md`
- `backend/app/modules/fees/schemas.py`
- `backend/tests/test_b_oa_fee_item_list_schema.py`
- `artifacts/BE-B-OA-FEE-ITEM-LIST-SCHEMA-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/fees/schemas.py tests/test_b_oa_fee_item_list_schema.py
python3 -m ruff format app/modules/fees/schemas.py tests/test_b_oa_fee_item_list_schema.py
python3 -m ruff check app/modules/fees/schemas.py tests/test_b_oa_fee_item_list_schema.py
pytest tests/test_b_oa_fee_item_list_schema.py -q
pytest tests/test_b3_fee_linking.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-B-OA-FEE-ITEM-LIST-SCHEMA-01
```

## Evidence Path

- `artifacts/BE-B-OA-FEE-ITEM-LIST-SCHEMA-01/results.jsonl`
- `artifacts/BE-B-OA-FEE-ITEM-LIST-SCHEMA-01/summary.md`
- `artifacts/BE-B-OA-FEE-ITEM-LIST-SCHEMA-01/git/diff.patch`
