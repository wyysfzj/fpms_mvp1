# FR-COM-03 Alembic Single-Head Prerequisite Design

**Feature:** `FR-COM-03` blocker prerequisite for Alembic single-head recovery

**Source of truth:**
- `docs/superpowers/specs/2026-03-28-fr-com-03-multi-agent-split-design.md`
- `docs/superpowers/plans/2026-03-28-fr-com-03-multi-agent-split.md`

## Story Shape Classification

- shared_file_density: `low`
- prereq_dependency_density: `medium`
- be_fe_coupling: `backend-only`
- evidence_cost: `low`

## Chosen Runbook

- chosen_runbook: `P0-single-lane-story`

**Problem Statement**

`FRCOM03-BE-COM-01` is blocked by the repository's Alembic migration graph, not by the commission split logic itself. The repo currently has two migration heads, so `backend/tests/conftest.py` cannot execute `command.upgrade(config, "head")` deterministically during pytest setup. This prerequisite must restore the graph to a single head so existing test fixtures can run unchanged.

**In Scope**

- Add exactly one Alembic merge revision that merges the current two heads into a single head.
- Keep the merge revision SQLite-safe and DDL-free except for graph merge metadata.
- Verify `cd backend && alembic heads` returns one head.
- Verify `cd backend && alembic upgrade head` succeeds against a fresh SQLite DB.

**Explicit Non-Scope**

- Editing `backend/app/modules/commission/service.py`
- Editing `backend/tests/test_commission_e2e.py`
- Editing `backend/tests/conftest.py`
- Rewriting existing migration contents or changing prior `down_revision` history
- Any frontend or API behavior changes

**Recommended Design**

Use a dedicated empty merge revision that declares both current heads as its `down_revision` parents. This preserves migration history, aligns with normal Alembic practice, and restores the single-head assumption expected by the repo's current test fixture.

**Compatibility Assessment**

- SQLite PoC compatibility: safe, because the merge revision does not introduce dialect-specific DDL.
- Existing pytest fixture compatibility: restored, because `upgrade(..., "head")` will once again resolve to one terminal revision.
- Shared ownership impact: limited to `backend/alembic/versions/*`, so execution must remain serialized.

**Design Conclusion**

- `可在当前约束下拆成可执行原子任务`

**Story-Level Closure Slice**

- Restore the repo Alembic graph to a single head using one merge revision so blocked FR-COM-03 commission tests can run against the existing fixture contract.

**Story-Level Non-Closure Boundary**

- Does not implement or modify any FR-COM-03 business behavior; it only removes the migration-graph blocker.
