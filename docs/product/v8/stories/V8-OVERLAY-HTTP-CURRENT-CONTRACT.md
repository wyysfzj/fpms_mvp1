# Story V8-OVERLAY-HTTP-CURRENT-CONTRACT

- Risk: `PROTECTED`
- Outcome: close catalog row `265` with the sole bodyless lifecycle-overlay GET adapter.
- Catalog ID: `FPMS-V8-OVERLAY-HTTP-20260712-01`.
- Authority: the row-265 Ultra freeze; this story binds its exact contract to C3 delivery.
- Dependency: begin only after the row-264 keyset successor is independently accepted.

## Exact adapter

Add `GET /cases/{case_id}/lifecycle-overlay` to the already-wired cases router. Inject
`Case.Read`, `Doc.Read`, `Task.Read` and `Fee.Read` as four separate handler parameters. Require
`after_sequence` and `limit`; accept omitted `as_of_revision` as null. FastAPI owns missing/type
validation (422), while typed integer values—including semantic range errors—pass unchanged to
the accepted service, which retains its frozen 400 behavior. Do not introduce HTTP defaults or a
second maximum that could diverge from the service contract.

Return `LifecycleOverlay` directly with 200. Pass the exact path/query values and caller session
to `read_lifecycle_overlay`; add no body, success envelope, serializer, clock, cursor calculation,
transaction control, resolver call or error remapping. Existing authentication, permission and
global error handling retain 401/403/404/409/422 status and envelope semantics.

## Serialization and verification

Every page serializes all 29 ordered gate entries unchanged: seven case-scoped codes and 22
distinct legacy composite identities. Never deduplicate by code. Preserve requested individual
form scopes, a possible resolved `ALL-22`, all source fields, `generated_at`, revision and cursor
values exactly.

The focused API test proves the sole route and no body, four independent permissions, exact
service arguments/session, direct two-page serialization, 29-entry identities/fallback, no
adapter writes or clock, and 401/403/404/409/422 behavior. Run scoped Ruff/format/diff and
independent High review.

No router wiring, service/schema/frontend change, partial-visibility variant, endpoint default,
query range policy or adjacent cleanup. Rollback reverts only the row-265 API/test change and its
adoption.
