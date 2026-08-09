# Story V8-DIRECT-CASE-STATUS-WRITE-GATE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Contract commit: `283ba2a`.
- Test commits: `7fce9fb`, `8068529`, `465ea2f`.
- Catalog ID: `FPMS-V8-DIRECT-STATUS-WRITE-STATIC-GATE-20260712-01` (ordinal `258`).
- Outcome: a read-only AST guard fails closed when production adds or weakens a direct write
  to the legacy compatibility field `Case.status`.

The guard permits exactly the lifecycle append projection and the accepted row-56 legacy-only
CAS. It asserts the append projection values and the CAS original-status plus five lifecycle
carrier-null predicates. Direct chained and bound ORM updates, keyword-unpacked status values,
query updates, statically identifiable instance assignments, and simple multi-hop statement
aliases are detected. The explicit legacy importer remains authorized only through delegation
to the lifecycle append seam; it owns no direct write.

The initial static RED exposed the missing guard. Independent review rejected two candidates
for bound/query/keyword-unpack and then simple alias fail-open paths. The final two-test focused
suite passed without loading repository SQLite; scoped Ruff, format and diff checks passed. The
corrected three-commit range was independently approved with P0/P1/P2 all zero.

No product source, runtime behavior, importer, schema, old task/evidence system or generalized
owner discovery is changed. Rollback reverts only the three test commits and this adoption.
