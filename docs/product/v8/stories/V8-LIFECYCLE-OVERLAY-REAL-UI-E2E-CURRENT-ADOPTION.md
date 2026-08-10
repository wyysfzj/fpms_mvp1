# Story V8 Lifecycle Overlay Real UI E2E Current Adoption

- Risk: `PROTECTED`.
- Product commits: `f7559cf`, `f5fca89`, `d8960b2`.
- Catalog owner: `FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01`.

The one-worker Playwright scenario seeds the dedicated live fixture, signs in through the real
Vite UI, opens the real case-detail route, and passively observes FastAPI responses backed by an
isolated migrated SQLite database. It installs no route handler and fulfills no application
response. Login, case and all overlay responses are verified as real JSON traffic without writing
response bodies or access tokens to assertion evidence.

The proof locks the exact first request and two continuation cursors, stable revision, 200/200/1
milestone pages, all three lanes, and the complete ordered 29-entry composite gate snapshot in
both network responses and the rendered DOM after every page. It also proves `ALL-22` fallback
provenance, independent unresolved visibility, and exact `仅供参考` / `非激活` presentation with no
activation control.

The original RED proved the missing spec. Final isolated real-stack Playwright passed one test in
4.2 seconds; standalone TypeScript and exact diff checks passed. Independent High review approved
the final candidate with P0/P1/P2 all zero.
