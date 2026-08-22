# V8 Full Terminal Dependency Successor Contract

Status: `CURRENT IMPLEMENTATION — INDEPENDENT PROTECTED REVIEW REQUIRED`

## Exact outcome and authority boundary

This Git-native successor adds one immutable dependency overlay without changing the frozen
catalog. It closes only the omitted Full-terminal ordering between catalog Rows 278, 281 and
282:

- Row281 adds Row278;
- Row282 adds Row278;
- Row282 adds Row281.

The resulting terminal order is exactly Row278 → Row281 → Row282 → Row283. The overlay is
additive only: it cannot remove, reorder, discover, wildcard or generalize any dependency. The
frozen catalog remains the sole authority for gate requirements, owner role, serialization
groups, phase and task path.

The protected catalog input remains pinned to SHA-256
`72c849825c9cbd39cb25f743d448b67a2a31bfccf7cfb68a3d2557c7bda178bf`.
Task cards may receive reviewed latest-wins appendices, so their mutable file bytes are not
duplicatively pinned here. Current task and product bytes are bound by reachable Git commits
and exact coverage-story tree fingerprints.

## Exact contract and validation

`docs/product/v8/full-terminal-dependency-successor.json` has schema version 1 and exactly
these top-level fields: `schema_version`, `catalog_sha256`, `base_dependency_sha256`,
`dependency_overlays`, `effective_dependency_sha256`,
`row283_dependency_sha256`, `effective_order`, and `deferred_coverage`. Each overlay object
contains only `target_task_id` and `add`; a removal field is invalid. Extra fields, targets,
edges or changed order fail closed.

The base dependency hashes for Rows 281 and 282 are both
`5800da16f9408789bd14370c40fe03264890f0bd46f76ad2070ed3404351ee5d`. Appending only the
three approved edges produces effective hashes
`6b17123b63d5a862a5f702454e38d2bab1e5a41512a4ed177b79957946c362b7` for Row281 and
`4369ee52400b52b368f66f2c447bf78b4d4c786834c1c74108c11ac13d70387b` for Row282.
Row283 remains the exact ordered list of all 282 predecessors with unchanged hash
`bbba116012490f9117f9fb68c539b45d0d8666733a77febbd0197076fb328e82`.

Before milestone validation, the lean coverage checker now validates the default contract path
and proves all of the following against the exact catalog bytes:

- Rows 281 and 282 effectively cover all 53 rows whose `deferred_kind` is `gated_product` or
  `legacy_form`;
- Row282 contains Row281 and every effective Row281 dependency;
- the complete effective catalog dependency graph remains acyclic;
- Row283 remains all exact 282 predecessors;
- base dependencies, effective dependencies and the catalog match their pinned hashes;
- the overlay carries no duplicate authority for gate, owner, serialization, phase or task
  path, and the catalog supplies each of those fields.

The integrated latest-owner byte comparison excludes only
`docs/product/v8/coverage-ledger.json`, whose metadata necessarily advances when later stories
are adopted. Historical candidate fingerprints still include the ledger where declared, and
all product-owned paths retain latest-review drift protection.

## Targeted TDD evidence

RED was captured before the contract or validator existed:

```text
python3 -m pytest -q scripts/tests/test_v8_lean_coverage_check.py -k full_terminal_dependency_successor_accepts_exact_overlay
1 failed, 28 deselected in 0.04s
AttributeError: module 'v8_lean_coverage_check' has no attribute 'validate_full_terminal_dependency_successor'
```

After the minimum contract and validator were added, the complete focused successor tranche was
GREEN:

```text
python3 -m pytest -q scripts/tests/test_v8_lean_coverage_check.py -k full_terminal_dependency_successor
17 passed, 12 deselected in 0.07s
```

The original focused tranche covered the exact pass case; each missing edge; extra edge, target,
field and removal; catalog, base and effective hash drift; exact 53/53 deferred coverage; Row281
inclusion; cycle rejection; and the unchanged Row283 sentinel. The Git-native successor adds a
regression proving that an unreviewed change to a terminal task card is rejected by its accepted
story owner fingerprint.

Fresh implementation verification before the protected commit also recorded:

```text
python3 -m pytest -q scripts/tests/test_v8_lean_coverage_check.py
29 passed in 1.01s

python3 -m ruff check scripts/v8_lean_coverage_check.py scripts/tests/test_v8_lean_coverage_check.py
All checks passed!

python3 scripts/v8_lean_coverage_check.py --milestone inventory
PASS: V8 coverage ledger (inventory)

git diff --check -- <the exact four-file allowlist>
exit 0
```

## Allowlist, non-closure and rollback

The implementation allowlist is exactly:

- `docs/product/v8/stories/V8-FULL-TERMINAL-DEPENDENCY-SUCCESSOR-CONTRACT.md`;
- `docs/product/v8/full-terminal-dependency-successor.json`;
- `scripts/v8_lean_coverage_check.py`;
- `scripts/tests/test_v8_lean_coverage_check.py`.

No catalog, coverage ledger, product source, task file, `backend/uv.lock`, retired
`v8_catalog_manifest_gate.py`, milestone disposition, owner discovery, legal/customer/source
fact, schema, migration or release behavior is changed. Independent PROTECTED review and
verification remain required; this implementer does not approve its own work.

Rollback reverts only the single successor commit, removing the additive contract, its focused
tests and the pre-milestone validator call. The frozen catalog and every base dependency remain
untouched.
