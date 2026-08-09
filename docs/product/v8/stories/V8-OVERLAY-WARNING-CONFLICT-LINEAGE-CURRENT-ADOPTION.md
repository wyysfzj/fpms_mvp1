# Story V8 Overlay Warning Conflict Lineage Current Adoption

- Risk: `PROTECTED`.
- Product commits: `850422a`, `afb7bd6`, `2896860`, `edf47dc`, `40ed8ed`.
- Successor contract: `V8-OVERLAY-WARNING-CONFLICT-LINEAGE-SUCCESSOR-CONTRACT`.

Lifecycle activity conflict codes now have same-case child rows and a parent version/count/hash
attestation. Append writes both atomically, replay reads the persisted attestation without
autoflush or identity-map trust, and missing, stale, partial or corrupt lineage fails closed.
The forward-only Delta-31 migration attests known-empty producers, backfills only the complete
legacy-import identity, and leaves pre-carrier patent-register and every legacy near-miss
unattested.

The real overlay now emits ordered activity, conflict, unresolved-gate and reference-only
warnings with exact provenance. Activity and legacy-conflict parts remain page-local; the complete
29-gate suffix is rebuilt on every page. Only the full, first-lifecycle legacy-import identity can
enter `legacy_conflicts`; malformed or later look-alikes remain ordinary warnings. The projection
is SELECT-only and changes no lifecycle, legal, fee or decision-gate state.

Focused RED proved the absent carrier/projection. Final focused and affected overlay verification
passed 92 tests; lifecycle append/register/legacy regressions passed 188 tests. Scoped Ruff,
Alembic single-head and diff checks passed. Two independent High review axes approved the final
candidate with P0/P1/P2 all zero.
