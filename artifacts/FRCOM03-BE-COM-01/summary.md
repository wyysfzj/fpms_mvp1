# FRCOM03-BE-COM-01 Evidence Summary

- Exact closure slice: `apply_commission_for_bill()` uses current effective `agent_splits` to split total commission into per-agent rows, preserves single-agent fallback, rewrites only unfrozen rows, and deletes rewritable stale rows when a split member is removed.
- Non-closure respected: no API changes, no billing-service changes, no schema/model changes, no settlement/report contract changes, no historical rewrite work.
- Verification:
  - `cd backend && ruff check app/modules/commission/service.py tests/test_commission_e2e.py` passed.
  - `cd backend && pytest -q tests/test_commission_e2e.py -k 'manual_bill or multi_agent_split'` passed (`2 passed, 2 deselected`).
  - `./scripts/task_validate.sh FRCOM03-BE-COM-01` passed.
- Test isolation note:
  - The split rewrite regression test now uses its own non-overlapping rule effective window so it does not collide with the pre-existing manual bill test in the session-scoped SQLite DB.
