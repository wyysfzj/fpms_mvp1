# BL-E2E-ANNUITY-TARGETED-GENERATION-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

For a granted case with required grant/annuity fields, support targeted annuity task generation and case-number query so the generated tasks can be found visibly by case number.

## Explicit Non-Closure

- Do not bypass the GRANTED prerequisite.
- Do not change grant-fee task status transitions in this task.
- Do not change frontend annuity dialog in this task.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `backend/app/modules/annuity/api.py`
- `backend/app/modules/annuity/service.py`
- `backend/app/modules/annuity/schemas.py`
- `backend/tests/test_annuity_targeted_generation_api.py`
- `tasks/backend/business_logic/BL-E2E-ANNUITY-TARGETED-GENERATION-01.md`
- `artifacts/BL-E2E-ANNUITY-TARGETED-GENERATION-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BL-E2E-ANNUITY-TARGETED-GENERATION-01 test /bin/zsh -lc 'cd backend && pytest -q tests/test_annuity_targeted_generation_api.py'
```

```bash
./scripts/evidence_run.sh BL-E2E-ANNUITY-TARGETED-GENERATION-01 lint /bin/zsh -lc 'cd backend && ruff check --fix app/modules/annuity/api.py app/modules/annuity/service.py app/modules/annuity/schemas.py tests/test_annuity_targeted_generation_api.py && ruff format app/modules/annuity/api.py app/modules/annuity/service.py app/modules/annuity/schemas.py tests/test_annuity_targeted_generation_api.py && ruff check app/modules/annuity/api.py app/modules/annuity/service.py app/modules/annuity/schemas.py tests/test_annuity_targeted_generation_api.py'
```

```bash
./scripts/evidence_run.sh BL-E2E-ANNUITY-TARGETED-GENERATION-01 task_gate ./scripts/task_validate.sh BL-E2E-ANNUITY-TARGETED-GENERATION-01
```

## Evidence Path

- `artifacts/BL-E2E-ANNUITY-TARGETED-GENERATION-01/results.jsonl`
- `artifacts/BL-E2E-ANNUITY-TARGETED-GENERATION-01/summary.md`
- `artifacts/BL-E2E-ANNUITY-TARGETED-GENERATION-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- `FE-E2E-ANNUITY-TARGETED-GENERATION-01`

