# BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Provide the local MVP1 demo/E2E prerequisite for grant-fee notice generation: an idempotent, SQLite-compatible `GRANT_FEE_NOTICE` document-template source configuration that lets a UI-created grant-fee task generate the authorization-fee notice through the visible grant-fee UI.

## Explicit Non-Closure

- Do not change grant-fee state-machine rules.
- Do not bypass the UI final retry with API business mutations.
- Do not modify Skeleton Pack assets.
- Do not change database schema or Alembic migrations.
- Do not implement annuity, payment, bill, or commission behavior in this task.

## Allowed Files

- `backend/scripts/seed_dev.py`
- `backend/tests/test_grant_fee_notice_template_source_seed.py`
- `backend/storage/templates/grant_fee_notice.docx`
- `tasks/backend/business_logic/BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01.md`
- `artifacts/BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01 test /bin/zsh -lc 'cd backend && source .venv/bin/activate && pytest -q tests/test_grant_fee_notice_template_source_seed.py'
```

```bash
./scripts/evidence_run.sh BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01 lint /bin/zsh -lc 'cd backend && source .venv/bin/activate && ruff check --fix scripts/seed_dev.py tests/test_grant_fee_notice_template_source_seed.py && ruff format scripts/seed_dev.py tests/test_grant_fee_notice_template_source_seed.py && ruff check scripts/seed_dev.py tests/test_grant_fee_notice_template_source_seed.py'
```

```bash
./scripts/evidence_run.sh BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01 secret_scan /bin/zsh -lc 'p1=admin"123"; p2="Authorization: ""Bearer"; p3=access"_token"; p4="ey""J[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"; ! rg -n "$p1|$p2|$p3|$p4" artifacts/BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01'
```

```bash
./scripts/evidence_run.sh BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01 task_gate ./scripts/task_validate.sh BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01
```

## Evidence Path

- `artifacts/BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01/results.jsonl`
- `artifacts/BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01/summary.md`
- `artifacts/BL-E2E-GRANT-FEE-NOTICE-TEMPLATE-SOURCE-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- `BATCH-DEMO-E2E-REAL-UI-FULL-RETRY-02`
