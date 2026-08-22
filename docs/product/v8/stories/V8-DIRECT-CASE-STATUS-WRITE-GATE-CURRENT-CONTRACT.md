# Story V8-DIRECT-CASE-STATUS-WRITE-GATE-CURRENT-CONTRACT

- Risk: `PROTECTED`
- Outcome: close catalog row `258` with a static, fail-closed guard against new direct
  writes to the compatibility field `Case.status`.
- Catalog ID: `FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01`.
- Base: `966e081c6628c45819a0cac79d80a8eb1974f137`.

## Authority reconciliation

The row-258 task summary predates the accepted row-56 legacy update contract. Row 56
explicitly preserves one direct legacy status transition while all five lifecycle carriers
are SQL `NULL`, protected by a conditional CAS. Removing or rejecting that write would
contradict a current verified dependency and break legacy cases.

The static gate therefore recognizes exactly two product write sites, not a generalized
owner-discovery rule:

1. `backend/app/modules/cases/lifecycle_activity_service.py` may project the compatibility
   status inside the sole append seam together with lifecycle axes and revision; and
2. `backend/app/modules/cases/service.py` may perform the accepted row-56 legacy-only CAS in
   `update_case_full`, whose predicate includes original status and SQL-nullity of all five
   lifecycle carriers.

The explicit legacy import is not a third direct-write site: it delegates to the first site.
This preserves the old row wording's import permission without duplicating write authority.

## Exact closure and test

Add only `backend/tests/test_v8_direct_case_status_write_gate.py`. The test parses production
Python with `ast`, locates writes whose target is specifically `Case.status`, and compares
their normalized structural identities to the two exact approved sites above. It must catch
ORM `update(Case).values(status=...)`, attribute assignment to a `Case` instance when
statically identifiable, and bulk update mappings keyed by `Case.status`. Any additional,
missing, moved, or structurally weakened site fails closed and requires a separately reviewed
successor contract; path or function-prefix discovery is forbidden.

The test also asserts the row-56 CAS retains the original-status predicate and all five
carrier-null predicates, and that the lifecycle append write remains in
`append_case_activity`. It is a read-only static test and does not initialize SQLite.

Verification is the focused pytest, scoped Ruff check-only/format-check, and exact diff
check. Because lifecycle compatibility is protected, an independent High reviewer must
review the exact commit and independently rerun the decisive checks.

## Non-goals and rollback

No product behavior, source module, schema, importer, lifecycle rule, task file, old evidence,
or broad repository audit changes. Do not infer permission from filename, directory, class
name, or call graph. Rollback removes only the static test and this story contract.
