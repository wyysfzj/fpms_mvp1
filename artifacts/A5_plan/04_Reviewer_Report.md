# A5 Batch — Review Report

## Summary

A5 adds six new Query parameters (`case_type`, `patent_category`, `flow_dir`, `filing_date_from`, `filing_date_to`, `primary_agent_id`) to both `GET /cases` and `GET /cases/export` endpoints. The same six parameters are propagated to `service.py list_cases()`. Seven new tests validate each filter individually, combined AND logic, and export parity.

## Acceptance Criteria

| # | Criterion | Pass/Fail | Notes |
|---|-----------|-----------|-------|
| 1 | GET /cases accepts 6 new Query params: case_type, patent_category, flow_dir, filing_date_from, filing_date_to, primary_agent_id | **PASS** | Lines 29-34 in api.py |
| 2 | GET /cases/export has the same 6 params (mirrored) | **PASS** | Lines 367-372 in api.py — identical param names/types |
| 3 | All filters are optional (default=None) | **PASS** | All use `Query(default=None)` |
| 4 | String filters use exact match (==) | **PASS** | `case_type`, `patent_category`, `flow_dir`, `primary_agent_id` all use `==` (lines 84-89, 94-95) |
| 5 | Date filters use >= and <= on Case.filing_date | **PASS** | `filing_date_from` → `>=`, `filing_date_to` → `<=` (lines 90-93) |
| 6 | Response schema NOT changed | **PASS** | Return dicts in both endpoints unchanged — same keys as before A5 |
| 7 | service.py list_cases() synced with same params | **PASS** | Lines 67-72 add the 6 params; filter logic at lines 93-104 matches api.py |
| 8 | 7 tests pass (case_type, patent_category, flow_dir, primary_agent_id, filing_date_range, combined, export) | **PASS** | `pytest tests/test_case_search.py -v` → 7 passed |
| 9 | ruff check passes | **PASS** | `ruff check` → "All checks passed!" |
| 10 | Full suite: 79 tests pass | **PASS** | `pytest --tb=short` → 79 passed in 17.31s |

## Code Quality

- **Lint**: `ruff check` — all checks passed (only deprecation warnings in pyproject.toml format, not A5-related)
- **Tests**: 7/7 A5-specific tests pass; 79/79 full suite passes — zero regressions
- **Code style**: Consistent with existing filter patterns (exact match via `==`, date range via `>=`/`<=`)
- **Test isolation**: Uses `_COUNTER` global for unique case_no generation — adequate for function-scoped fixtures

## Issues Found

- **None** — implementation is clean and matches all acceptance criteria exactly.

## Observations (non-blocking)

1. `api.py` duplicates filter logic between `GET /cases` and `GET /cases/export` rather than delegating to `service.list_cases()`. This is pre-existing technical debt (not introduced by A5) and out of scope for this batch.
2. The test helper `_set_filing_date` directly accesses the DB via `app.dependency_overrides` — functional but tightly coupled to test infrastructure. Acceptable for PoC stage.

## Verdict

**APPROVED**
