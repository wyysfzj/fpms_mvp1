# BE-A-COMMISSION-RULE-SEED-READINESS-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: BE-A-COMMISSION-RULE-SEED-READINESS-01
- Role: worker
- Runbook: P0-prereq-heavy-story

## Exact Closure Slice

Verify or minimally fix commission rule arrange path and generated commission semantics required by `TC-A-023`.

This task closes only:

1. NORMAL commission rule can be arranged through existing API/service/fixture.
2. Main/co-agent source is clear and stable.
3. Service fee base is used.
4. S1/S2 amounts are calculated.
5. 70/30 split is respected if contract/model supports it.
6. WaitPay / ForceSettle initial values are stable.
7. Available-to-settle query path is visible.

## Explicit Non-Closure

This task does not:

- implement settlement execution
- implement pytest automation handlers
- modify billing behavior
- modify frontend or skeleton data

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-COMMISSION-P0-01

## Allowed Files

- tasks/backend/business_logic/BE-A-COMMISSION-RULE-SEED-READINESS-01.md
- backend/app/modules/commission/service.py
- backend/app/modules/commission/api.py
- backend/app/modules/commission/schemas.py
- backend/tests/test_commission_rule_seed_readiness.py
- artifacts/BE-A-COMMISSION-RULE-SEED-READINESS-01/**

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/commission/service.py app/modules/commission/api.py app/modules/commission/schemas.py tests/test_commission_rule_seed_readiness.py
python3 -m ruff format app/modules/commission/service.py app/modules/commission/api.py app/modules/commission/schemas.py tests/test_commission_rule_seed_readiness.py
python3 -m ruff check app/modules/commission/service.py app/modules/commission/api.py app/modules/commission/schemas.py tests/test_commission_rule_seed_readiness.py
pytest tests/test_commission_rule_seed_readiness.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-A-COMMISSION-RULE-SEED-READINESS-01
```

## Evidence Path

- artifacts/BE-A-COMMISSION-RULE-SEED-READINESS-01/results.jsonl
- artifacts/BE-A-COMMISSION-RULE-SEED-READINESS-01/summary.md
- artifacts/BE-A-COMMISSION-RULE-SEED-READINESS-01/git/diff.patch
