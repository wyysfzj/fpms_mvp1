# B1 Batch -- Review Report

**Reviewer**: Review Agent
**Date**: 2026-02-25
**Batch**: B1 -- DocTemplate Enhancement + CRUD API

---

## Summary

Batch B1 adds SPEC configuration fields to the existing `DocTemplate` model and exposes a full CRUD API for managing doc templates. The implementation includes:

- An Alembic migration adding 8 new columns to `t_doc_template`
- 8 new mapped columns on the `DocTemplate` ORM model
- 4 Pydantic schemas (`DocTemplateCreateIn`, `DocTemplateUpdateIn`, `DocTemplateOut`, `DocTemplateListOut`)
- 4 service functions (`list_doc_templates`, `get_doc_template`, `create_doc_template`, `update_doc_template`)
- 4 API endpoints (`GET /doc-templates`, `POST /doc-templates`, `GET /doc-templates/{id}`, `PUT /doc-templates/{id}`)
- 3 new RBAC permissions (`DocTemplate.Read`, `DocTemplate.Create`, `DocTemplate.Edit`)
- Dev seed with 5 doc templates
- Test conftest seeding for 5 doc templates
- 14 comprehensive test cases

---

## Acceptance Criteria

| # | Criterion | Pass/Fail | Notes |
|---|-----------|-----------|-------|
| 1 | Migration runs cleanly on fresh DB (`rm -f fpms_dev.db && alembic upgrade head`) | PASS | Tested fresh DB: all 20 migrations applied cleanly including `b1_doc_tpl_01`. |
| 2 | `seed_dev.py` seeds 5 doc templates without errors | PASS | Output confirmed: "Created 5 doc templates". Codes: OA_IN, OA_OUT, ACCEPTANCE_NOTICE, GRANT_NOTICE, CLIENT_IN. |
| 3 | `GET /api/v1/doc-templates` returns seeded templates with SPEC fields | PASS | Test `test_list_doc_templates_returns_seeded` verifies OA_IN with `need_reply=True`, `status_effect="OA1"`, `deadline_template_code="OA_REPLY"`. |
| 4 | `POST /api/v1/doc-templates` creates template with all fields; returns 201 | PASS | Test `test_create_doc_template` sends all 12 fields, verifies 201 and correct response body. |
| 5 | `POST /api/v1/doc-templates` with duplicate code returns 409 | PASS | Test `test_create_doc_template_duplicate_code_rejected` verifies 409 with error code `DOC_TEMPLATE_CODE_EXISTS`. |
| 6 | `GET /api/v1/doc-templates/{id}` returns single template; 404 for missing | PASS | Tests `test_get_doc_template_by_id` (200) and `test_get_doc_template_not_found` (404 with `DOC_TEMPLATE_NOT_FOUND`). |
| 7 | `PUT /api/v1/doc-templates/{id}` updates partial fields; returns 200 | PASS | Tests `test_update_doc_template` and `test_update_doc_template_partial` both verify partial update with unchanged fields preserved. |
| 8 | `PUT /api/v1/doc-templates/{id}` for missing ID returns 404 | PASS | Test `test_update_doc_template_not_found` verifies 404 with correct error code. |
| 9 | Direction/enabled/q filters work on list endpoint | PASS | Tests `test_list_doc_templates_filter_direction`, `test_list_doc_templates_filter_enabled`, `test_list_doc_templates_search_q` all pass. |
| 10 | Pagination works (page, page_size, total) | PASS | Test `test_list_doc_templates_pagination` verifies page/page_size/total and non-overlapping page items. |
| 11 | Unauthenticated requests return 401 | PASS | Test `test_doc_template_unauthorized` checks all 4 endpoints without auth token. |
| 12 | Admin role has all 3 DocTemplate permissions | PASS | `rbac/service.py` lines 33-35: `DocTemplate.Create`, `DocTemplate.Edit`, `DocTemplate.Read` in Admin role. |
| 13 | Formalities role has DocTemplate.Read | PASS | `rbac/service.py` line 81: `DocTemplate.Read` in Formalities role. |
| 14 | All existing tests still pass (`pytest --tb=short`) | PASS | Full suite: 93 tests passed, 0 failures. |
| 15 | `ruff check` passes with no errors | PASS | Output: "All checks passed!" (with deprecation warnings for pyproject.toml config keys, which are pre-existing and unrelated to B1). |
| 16 | Existing Document CRUD endpoints continue to work unchanged | PASS | Document endpoints in `api.py` (lines 116-437) are unchanged. Existing Document tests in `test_flows.py` continue to pass. |

---

## Code Quality

### Lint Results
- `ruff check .` -- All checks passed. No lint errors.
- Pre-existing deprecation warnings in pyproject.toml (top-level lint config keys) are unrelated to B1.

### Test Results
- **B1 tests**: 14/14 passed in 4.10s
- **Full suite**: 93/93 passed in 21.31s
- No warnings introduced by B1 code (existing Pydantic deprecation warnings from `auth/schemas.py` and `cases/schemas.py` are pre-existing).

### Code Style Observations
- Code follows established project patterns consistently.
- `DocTemplateOut` uses `model_config = ConfigDict(from_attributes=True)` for ORM-to-Pydantic conversion -- cleaner than the manual field mapping used by `DocumentOut`. This is the recommended pattern from the architect plan.
- API endpoints are placed before `/documents/{document_id}` routes, correctly avoiding route conflict. This is clearly annotated with a section comment.
- Service functions follow the same pattern as existing `templates/service.py` (list/get/create/update).
- Migration uses `batch_alter_table` and idempotent column checks, consistent with the `a1_task_template_fields.py` pattern.
- Seed functions are idempotent with proper duplicate checking.
- Test helper `_unique_code()` generates UUID-based codes to avoid cross-test collisions.

---

## Issues Found

**None.** No bugs, missing features, or correctness issues were identified.

---

## Observations (non-blocking)

1. **DocTemplateUpdateIn allows clearing SPEC fields to None**: Because all SPEC fields default to `None` in `DocTemplateUpdateIn`, a client must use `exclude_unset=True` (which the service does correctly) to distinguish between "field not sent" and "field explicitly set to null". The current implementation handles this correctly via `data.model_dump(exclude_unset=True)` in `update_doc_template()`.

2. **`direction` enum stored as raw string in model**: The `DocTemplate.direction` model field is `Mapped[str]` rather than `Mapped[DocumentDirection]`. This is consistent with the existing `Document` model and works correctly because the Pydantic schema uses `DocumentDirection` for validation. The ORM stores/retrieves the string value, and `from_attributes=True` handles the conversion.

3. **`need_reply` typed as `bool | None` in schema**: The `DocTemplateOut.need_reply` field is `bool | None`, matching the model's nullable column. For seeded templates that do not explicitly set `need_reply`, the DB default `server_default=text("0")` will produce `False`. This is correct behavior.

4. **JSON text fields**: `fee_item_list` and `input_fields` store JSON as plain `Text` with no schema-level JSON validation. This is an intentional B1 design decision documented in the architect plan (section 12). Application-level validation of these fields is deferred to B2/B3.

5. **`enabled` filter value type**: The `list_doc_templates` service function checks `if enabled is not None` for the boolean filter, which correctly handles `enabled=False` (a falsy but non-None value). This is correct.

6. **Pre-existing issue in `DocumentOut`**: The existing `DocumentOut` class does not have `from_attributes=True` and uses manual field mapping in the API layer. This inconsistency pre-dates B1 and is not a B1 concern.

---

## Verdict

**APPROVED**

All 16 acceptance criteria pass. The implementation is clean, well-structured, and consistent with existing project patterns. Migration runs cleanly on fresh DB, all 93 tests pass (including 14 new B1 tests), ruff check passes, and no bugs were found. The code is ready for integration.
