# Story V8-OVERLAY-CONTRACTS-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the already-integrated lifecycle-overlay
  public schemas satisfy the exact frozen catalog row `259`.
- Change mode: current adoption only; no product or test byte changes because the
  untouched focused current-tree contract test already passes.
- Catalog ID: `FPMS-V8-OVERLAY-CONTRACTS-20260712-01` (ordinal `259`, profile
  `TC-INTERFACE`).
- Authority: the lifecycle, evidence-lineage, official-fee and customer-decision
  boundaries in `docs/product/v8/domain-contract.md`; frozen catalog row `259`; its exact
  task contract; and the latest-wins Delta-2 and Delta-3 contract freezes.
- Base: `e1957b3d77e4f54f20a695823b857bc25790ba82`.

## Dependencies

The canonical direct prerequisites remain:

1. `FPMS-V8-LC-CONTRACTS-20260712-01`;
2. `FPMS-V8-DE-CONTRACTS-20260712-01`;
3. `FPMS-V8-FO-CONTRACTS-20260712-01`;
4. `FPMS-V8-DECISION-GATE-RECORD-SERVICE-20260712-01`; and
5. `FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01`.

Delta-3 makes the RAW-role prerequisite depend directly on the RAW registration guard and
the external-submission positive-role guard. This overlay story inherits both guards only
transitively. It does not add either guard as a direct dependency or duplicate either
service rule.

## Exact closure

The current module exports the four exact ordered string enums and all fifteen frozen,
slotted, keyword-only DTOs for overlay query, center snapshot and changes, document
evidence, work packages and receipts, tasks, fee lines and obligations, warnings,
decision gates, legacy conflicts, milestones and the lifecycle-overlay response.

The schemas reuse the accepted lifecycle, document-evidence, fee-obligation and
decision-gate types by identity. Repeated values are tuples; `center_changes` is a
`Mapping`; fee amounts and reduction ratios remain wire strings; nullable fields remain
required constructor arguments.

The decision-gate collection is an ordered tuple with composite identity
`(gate_code, requested_scope_key)`. It preserves seven case-scoped entries plus
twenty-two ordered `LEGACY_FORM_CLASS` entries, including exact `form-NNN` request
identity when the accepted resolver returns `ALL-22` fallback provenance. A code-only
mapping or uniqueness rule cannot represent the contract. The response exposes one
`generated_at` timestamp and the exact revision/cursor fields; resolver, clock and keyset
behavior remain downstream.

`EvidenceRole.RAW_ATTACHMENT` remains intake-only classification carried through the
reused evidence result. It grants no overlay inclusion, document/formal-role meaning,
decision-gate authority or lifecycle-center authority. This story adds no RAW
applicability or authority rule.

## Exact paths and verification

- Product: `backend/app/modules/cases/lifecycle_overlay_schemas.py`
- Focused pure interface test:
  `backend/tests/test_v8_lifecycle_overlay_contracts.py`
- Story: `docs/product/v8/stories/V8-OVERLAY-CONTRACTS-CURRENT-ADOPTION.md`

The untouched focused test was run from this worktree's `backend` directory with:

```text
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_lifecycle_overlay_contracts.py
```

It returned `2 passed, 1 warning`; the warning is the existing passlib `crypt`
deprecation. The test remained a pure interface test and did not initialize or write
SQLite. Because the current contract was already GREEN, no RED was manufactured and no
product or test bytes changed.

Run scoped Ruff check-only on the exact product and focused-test paths, run exact
story-scope diff-check, and inspect the commit range and file list. An independent High
reviewer must review the exact commit and rerun the decisive checks. The implementer does
not approve this `PROTECTED` story; it remains pending independent review.

## Non-goals and rollback

No persistence, business adapter, resolver or join, applicability or aggregation rule,
endpoint, API serialization, UI, schema/migration, SQLite write, clock capture, keyset
implementation, customer-policy inference, direct RAW guard duplication, adjacent
catalog row, ledger/disposition/review edit, old task/evidence mutation or Foundation
claim. Rollback reverts only this story-card commit; the accepted product and test bytes
remain unchanged.
