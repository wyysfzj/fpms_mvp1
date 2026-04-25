# A-AUTO-PY-A-WAVE-CLOSE-SMOKE-MAINT-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Maintain existing A-wave automation setup so the final full-wave smoke can run after Batch 1-4 backend rules are active.

This task closes only:

1. TC-A-004 invalid-combo setup includes valid applicant prerequisites so applicant-list rules do not mask the target combo rule.
2. TC-A-011/012/013 batch-filing setup resets `APPLY_FEE_LIMIT` template to CASE_EVENT before submitted-date based checks.
3. TC-A-023 commission setup updates any conflicting existing NORMAL service rule to the expected wait/force flags.

## Explicit Non-Closure

Do not implement new testcase behavior, remove or add handlers, modify backend/frontend/skeleton data, or change TC-A-014/024 product assertions.

## Remaining Follow-Up Task IDs

- BATCH-A-WAVE-CLOSE-AUDIT-01

## Allowed Files

- tasks/automation/A-AUTO-PY-A-WAVE-CLOSE-SMOKE-MAINT-01.md
- FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
- artifacts/A-AUTO-PY-A-WAVE-CLOSE-SMOKE-MAINT-01/**

## Verification Commands

Run from `FPMS_Automation_Skeleton_Pack/pytest_python`:

```bash
python3 -m ruff check --fix handlers/wave_a.py
python3 -m ruff format handlers/wave_a.py
python3 -m ruff check handlers/wave_a.py
pytest tests/test_wave_a.py -k "TC-A-004 or TC-A-011 or TC-A-012 or TC-A-013 or TC-A-023" -q
```

## Evidence Path

- artifacts/A-AUTO-PY-A-WAVE-CLOSE-SMOKE-MAINT-01/results.jsonl
- artifacts/A-AUTO-PY-A-WAVE-CLOSE-SMOKE-MAINT-01/summary.md
- artifacts/A-AUTO-PY-A-WAVE-CLOSE-SMOKE-MAINT-01/git/diff.patch
