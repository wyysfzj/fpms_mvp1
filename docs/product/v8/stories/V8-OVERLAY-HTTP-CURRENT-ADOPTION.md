# Story V8-OVERLAY-HTTP-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Contract commit: `4157a7c`.
- Product/test commit: `646d460`.
- Catalog ID: `FPMS-V8-OVERLAY-HTTP-20260712-01` (ordinal `265`).
- Outcome: expose the accepted overlay as the sole direct bodyless cases GET endpoint.

The handler requires `after_sequence` and `limit`, accepts an optional revision, injects all four
read permissions independently and passes exact values plus the caller session to the service.
It returns the dataclass directly without a new envelope, clock, transaction, resolver, cursor
logic or error mapping. The complete ordered 29-gate tuple is serialized on every page.

The focused RED proved the missing route/service seam. GREEN passed 10 route, permission,
two-page serialization and 401/403/404/409/422 tests. Scoped Ruff, format and diff checks passed;
independent High review approved P0/P1/P2 all zero.

No router wiring, second endpoint, partial visibility, service/schema/frontend or adjacent change
is included. Rollback reverts the product/test commit and this adoption.
