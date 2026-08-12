# FPMS V8 Input Activation Capability Ledger Adoption

Status: `IMPLEMENTATION`
Risk: `PROTECTED`
Runbook: `P0-prereq-heavy-story`

## Observable outcome

Adopt the already implemented and independently reviewed payment-workbook and service-price
capabilities into the Git-native V8 coverage ledger without claiming that either production
input is configured. Exactly catalog rows 175, 176, 214–229 and 278 become
`CURRENT_VERIFIED` through story
`V8-INPUT-ACTIVATION-CAPABILITIES-CURRENT-ADOPTION`.

The story records `CAPABILITY_READY`, keeps
`DG-PAYMENT-WORKBOOK:GLOBAL` and `DG-SERVICE-RATE-VERSION:GLOBAL` as
`CONFIG_REQUIRED`, records `production_activation_claimed: false`, and preserves production
`409 / NO WRITE` plus TEST_ONLY isolation.

## Prerequisites

- Capability close commit `a8219b7a39047b819100cc69dd4cffadfc3e170c` is reachable and
  independently approved with P0/P1/P2 `0/0/0`.
- Row278 cumulative commits `6a17a18` and `97771c2`, plus integration successors
  `090b4b7`, `d2810c3` and `2280839`, are reachable and independently approved.
- The frozen catalog SHA-256 remains
  `72c849825c9cbd39cb25f743d448b67a2a31bfccf7cfb68a3d2557c7bda178bf`.

## Exact closure

1. Remove mutable task-file byte pins from the Full-terminal dependency successor. Preserve
   the frozen catalog hash, exact additive edges, dependency hashes, order and 53-row coverage.
   Current task bytes remain governed by reachable reviewed story fingerprints.
2. Exclude only `docs/product/v8/coverage-ledger.json` from integrated latest-owner byte
   comparison, because later ledger metadata adoption necessarily changes it. Historical
   candidate fingerprints, schema, row/story references and product owned-path drift checks
   remain enforced.
3. Add focused regressions proving ledger-only metadata changes pass while any product-owned
   byte drift still fails.
4. Add the exact 19-row adoption story and verify inventory against the adoption candidate.

## Non-closure

- Do not configure, approve or activate a real payment workbook or service price version.
- Do not change product source, API, schema, migration, UI or runtime behavior.
- Do not mark Row199, Row281, Row282, Row283, Full, Final or Release complete.
- Do not modify the frozen catalog or source-decision registry.
- Do not use or extend historical `docs/agents/**`, `scripts/taskctl`, canonical-scope or
  Evidence V2 machinery.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-CAPABILITY-LEDGER-ADOPTION-20260813-01.md`
- `docs/product/v8/stories/V8-INPUT-ACTIVATION-CAPABILITY-LEDGER-ADOPTION.md`
- `docs/product/v8/reviews/V8-INPUT-ACTIVATION-CAPABILITIES-CURRENT-ADOPTION.md`
- `docs/product/v8/coverage-ledger.json`
- `docs/product/v8/full-terminal-dependency-successor.json`
- `docs/product/v8/stories/V8-FULL-TERMINAL-DEPENDENCY-SUCCESSOR-CONTRACT.md`
- `scripts/v8_lean_coverage_check.py`
- `scripts/tests/test_v8_lean_coverage_check.py`
- `scripts/tests/test_v8_input_activation_capability_ledger_adoption.py`

`backend/uv.lock` is unrelated user dirt and must remain untouched.

## Verification

```text
python3 -m pytest -q scripts/tests/test_v8_lean_coverage_check.py scripts/tests/test_v8_input_activation_capability_ledger_adoption.py
python3 -m ruff check scripts/v8_lean_coverage_check.py scripts/tests/test_v8_lean_coverage_check.py scripts/tests/test_v8_input_activation_capability_ledger_adoption.py
python3 scripts/v8_lean_coverage_check.py --milestone inventory --integration-sha <candidate-sha>
git diff --check -- <exact allowlist>
```

## Acceptance and rollback

The implementation candidate requires independent High review of the exact commit/range with
P0/P1/P2 `0/0/0`. The reviewer verifies the focused tests, checker inventory result, exact
19-row mapping, capability/configuration separation and scope. Rollback reverts only this
story's checker/contract/adoption commits; it never changes product data or production inputs.
