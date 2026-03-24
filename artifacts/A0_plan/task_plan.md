# A0 Baseline Verification — Task Plan

## Objective
Verify the 4 MVP1 success criteria work end-to-end. Fix any blockers found. No new features.

## Steps
1. Setup backend (venv, deps, clean DB, migrate, seed)
2. Start server, verify healthz
3. Run verification script from Claude_enhance.md
4. Investigate/fix any failures
5. Run quality gate (ruff, pytest, alembic, seed, healthz)
6. Record results

## Status: COMPLETE
All criteria verified. Quality gate passed. 3 bugs fixed. Ready for A1.
