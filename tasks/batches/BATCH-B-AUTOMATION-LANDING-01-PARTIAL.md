# BATCH-B-AUTOMATION-LANDING-01-PARTIAL

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Land only the B-wave automation handlers that `BATCH-B-BLOCKER-DRAIN-02-CLOSE-AUDIT` marked ready and preserve honest BLOCKED status if real smoke exposes a hidden backend gap:

- `TC-B-001`
- `TC-B-002`
- `TC-B-003`
- `TC-B-004`
- `TC-B-006`
- `TC-B-007`
- `TC-B-008`
- `TC-B-009` was attempted but remains BLOCKED because the FeeItem query API returns 500 for wizard-created OA fee items.

Each testcase has its own atomic task file under `tasks/automation/`.

## Explicit Non-Closure

Do not implement `TC-B-005`, `TC-B-010`, `TC-B-011`, `TC-B-012`, or `TC-B-013`.
Do not modify backend, frontend, skeleton data, schemas, manifests, or Playwright assets.
Do not fake PASS when backend semantics are absent.

## Serialized Wave Order

1. `B-AUTO-PY-B-DOCUMENT-RECEIVE-P0-01`
2. `B-AUTO-PY-B-OA-DUE-DATE-P1-01`
3. `B-AUTO-PY-B-DOCUMENT-VALIDATION-P0-01`
4. `B-AUTO-PY-B-REPLY-TASK-P0-01`
5. `B-AUTO-PY-B-OA-REPLY-P0-01`
6. `B-AUTO-PY-B-REPLYTO-CONSTRAINT-P0-01`
7. `B-AUTO-PY-B-AUTO-WRITEOFF-P0-01`
8. `B-AUTO-PY-B-OA-FEE-DRAFT-P1-01` (BLOCKED, handler remains skeleton)

`FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py` is a shared ownership file and was edited serially.

## Allowed Files

- `tasks/batches/BATCH-B-AUTOMATION-LANDING-01-PARTIAL.md`
- `tasks/automation/B-AUTO-PY-B-*.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_partial_landing_handlers.py`
- `artifacts/BATCH-B-AUTOMATION-LANDING-01-PARTIAL/**`
- `artifacts/B-AUTO-PY-B-*/**`

## Verification Commands

From `FPMS_Automation_Skeleton_Pack/pytest_python`:

```bash
python3 -m ruff check handlers/wave_b.py tests/test_b_partial_landing_handlers.py
pytest tests/test_b_partial_landing_handlers.py -q
pytest tests/test_wave_b.py -k "TC-B-001 or TC-B-002 or TC-B-003 or TC-B-004 or TC-B-006 or TC-B-007 or TC-B-008 or TC-B-009" -q
pytest tests/test_asset_integrity.py tests/test_auth_client_smoke.py tests/test_db_assert.py tests/test_helpers_runid_enum.py tests/test_seed_data.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BATCH-B-AUTOMATION-LANDING-01-PARTIAL
```

## Evidence Path

- `artifacts/BATCH-B-AUTOMATION-LANDING-01-PARTIAL/results.jsonl`
- `artifacts/BATCH-B-AUTOMATION-LANDING-01-PARTIAL/summary.md`
- `artifacts/BATCH-B-AUTOMATION-LANDING-01-PARTIAL/git/diff.patch`

## Remaining Follow-Up Task IDs

- `BE-B-OA-FEE-ITEM-LIST-SCHEMA-01`
- `BATCH-B-BLOCKER-DRAIN-03`
- `BATCH-B-AUTOMATION-LANDING-02-REMAINDER`
- `BATCH-B-CLOSE-AUDIT-02`
