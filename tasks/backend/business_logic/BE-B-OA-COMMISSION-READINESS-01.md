# BE-B-OA-COMMISSION-READINESS-01

Task ID: `BE-B-OA-COMMISSION-READINESS-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Verify or minimally fix OA service-fee commission readiness for `TC-B-012`.

This task closes only:

1. OA bill with `SERVICE` fee item enters the commission pipeline.
2. Commission base fee, S1/S2 amounts, multi-agent split, wait-pay and query visibility are stable.
3. Existing commission behavior remains intact.

## Explicit Non-Closure

Do not implement pytest automation handlers.
Do not implement bill/payment readiness.
Do not add settlement execution behavior.
Do not modify frontend or skeleton data.

## Remaining Follow-Up Task IDs

- `B-AUTO-PY-B-OA-COMMISSION-P1-01`

## Allowed Files

- `tasks/backend/business_logic/BE-B-OA-COMMISSION-READINESS-01.md`
- `backend/app/modules/commission/service.py`
- `backend/app/modules/commission/api.py`
- `backend/tests/test_b_oa_commission_readiness.py`
- `artifacts/BE-B-OA-COMMISSION-READINESS-01/**`

If behavior is already supported, this may be a test/readiness-only task.

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/commission/service.py app/modules/commission/api.py tests/test_b_oa_commission_readiness.py
python3 -m ruff format app/modules/commission/service.py app/modules/commission/api.py tests/test_b_oa_commission_readiness.py
python3 -m ruff check app/modules/commission/service.py app/modules/commission/api.py tests/test_b_oa_commission_readiness.py
pytest tests/test_b_oa_commission_readiness.py -q
pytest tests/test_commission_waitpay_threshold.py tests/test_commission_rule_seed_readiness.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-B-OA-COMMISSION-READINESS-01
```

## Evidence Path

- `artifacts/BE-B-OA-COMMISSION-READINESS-01/results.jsonl`
- `artifacts/BE-B-OA-COMMISSION-READINESS-01/summary.md`
- `artifacts/BE-B-OA-COMMISSION-READINESS-01/git/diff.patch`
