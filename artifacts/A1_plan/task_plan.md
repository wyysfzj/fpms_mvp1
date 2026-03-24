# Batch A1 — Task Plan

## Batch: A1 — TaskTemplate Enhancement + TaskLog API
## Date: 2026-02-24
## Status: COMPLETED

## Objective
Make Doc→Task auto-generation work by:
1. Adding deadline calculation fields to TaskTemplate
2. Providing CRUD API for TaskTemplate
3. Adding a TaskLog read API
4. Seeding starter templates
5. Fixing TaskGenerationService to use the new fields

## Team Structure (Planned)
| Role | Agent | Responsibility |
|------|-------|---------------|
| Architect | team-lead | Plan decomposition, task assignment, coordination |
| Model Agent | model-agent | Migration + Model + Enum + Schema changes |
| API Agent | api-agent | Service + API + RBAC + Seed changes |
| Fix Agent | fix-agent | TaskGenerationService fix |
| Test Agent | test-agent | Write and run all tests |
| Review Agent | review-agent | Code review + report generation |

## Execution Note
> **Post-hoc note**: This batch was executed by a single agent without team coordination.
> Artifacts are generated retroactively. See findings.md for lessons learned.

## Task Decomposition

### Phase 1: Foundation (parallel)
| Task ID | File | Action | Assignee |
|---------|------|--------|----------|
| A1-01 | `alembic/versions/a1_task_template_fields.py` | NEW — add 5 columns migration | model-agent |
| A1-02 | `modules/tasks/models.py` | MODIFY — add 5 mapped columns | model-agent |
| A1-03 | `modules/tasks/enums.py` | MODIFY — add AUTO_CREATE_FROM_DOCUMENT | model-agent |

### Phase 2: API Layer (sequential, depends on Phase 1)
| Task ID | File | Action | Assignee |
|---------|------|--------|----------|
| A1-04 | `modules/tasks/schemas.py` | MODIFY — add 3 schemas | api-agent |
| A1-05 | `modules/tasks/service.py` | MODIFY — add 5 functions | api-agent |
| A1-06 | `modules/tasks/api.py` | MODIFY — add 4 endpoints | api-agent |
| A1-07 | `modules/rbac/service.py` | MODIFY — add TaskTemplate.* perms | api-agent |
| A1-08 | `scripts/seed_dev.py` | MODIFY — seed 2 templates | api-agent |

### Phase 3: Fix (parallel with Phase 2)
| Task ID | File | Action | Assignee |
|---------|------|--------|----------|
| A1-09 | `modules/tasks/task_generation_service.py` | MODIFY — fix _get_offset_days + internal_due_date | fix-agent |

### Phase 4: Verification (depends on all above)
| Task ID | File | Action | Assignee |
|---------|------|--------|----------|
| A1-10 | `tests/test_task_template.py` | NEW — 6 tests | test-agent |
| A1-11 | Quality Gate | ruff + pytest + alembic + seed + healthz | test-agent |
| A1-12 | Review Report | Code review + acceptance check | review-agent |

## Quality Gate
```bash
cd backend && source .venv/bin/activate
ruff check --fix . && ruff format .
ruff check .                          # must pass clean
pytest -q                              # all tests pass
rm -f fpms_dev.db && alembic upgrade head
python scripts/seed_dev.py
uvicorn app.main:app --port 8000 &
sleep 3 && curl -sf http://localhost:8000/healthz
kill %1
```
