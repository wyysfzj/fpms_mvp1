# BATCH-A-P1-COMPLETION-01

Batch ID: `BATCH-A-P1-COMPLETION-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high

chosen_runbook: `P0-prereq-heavy-story`

## Serialized Automation Landing Order

Start a testcase only after its readiness blockers PASS.

| Order | Task ID | Testcase | Task file path | Status at readiness |
| --- | --- | --- | --- | --- |
| 1 | `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01` | `TC-A-002` | `tasks/automation/A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01.md` | waiting on product/backend |
| 2 | `A-AUTO-PY-A-FOREIGN-COMBO-P1-01` | `TC-A-007` | `tasks/automation/A-AUTO-PY-A-FOREIGN-COMBO-P1-01.md` | waiting on product/backend |
| 3 | `A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01` | `TC-A-009` | `tasks/automation/A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01.md` | waiting on product/backend |
| 4 | `A-AUTO-PY-A-TASK_REASSIGN-P1-01` | `TC-A-014` | `tasks/automation/A-AUTO-PY-A-TASK_REASSIGN-P1-01.md` | PASS |

## Executed Automation Status

`TC-A-014` is landed through `A-AUTO-PY-A-TASK_REASSIGN-P1-01`.

The remaining three tasks must wait for product/backend blocker drain:

- `A-AUTO-PY-A-MINIMAL-REQUIRED-P1-01`
- `A-AUTO-PY-A-FOREIGN-COMBO-P1-01`
- `A-AUTO-PY-A-SPEC-FEE-DISCOUNT-P1-01`

## Shared File Serialization

`FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py` is a shared ownership file and must be edited by only one automation task at a time.

## Common Non-Closure

Automation tasks must not modify backend, frontend, skeleton YAML/JSON/manifest/schema, or Playwright assets. They must not fake backend behavior or use unrelated failures as target assertions.
