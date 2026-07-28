# FPMS C3.1 Lean Cutover Report

- Date: 2026-07-28
- Status: lean-governance adoption candidate; product adoption has not started
- Active branch: `codex/c3-lean-integration-20260728`
- Fixed clean parent: `afa58429e6b6e80b85f76055139e18fbe38ec9e8`

## Quarantine and archive

The original workspace remains a read-only quarantine. Its observed visible dirty state was
129 tracked modified paths plus 345 nonignored untracked paths, for 474 paths total. The
tracked diff was `+41,418/-6,157`.

The external restricted evidence archive is:

`/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic-c3-archive/20260728`

It contains 1,254 selected evidence files. Its checksum manifest SHA-256 is
`6d7804369b9558939c550fdd4c47132aded2a9b9583eba7dc4a8eead03200714`; the recorded
checksums verified successfully. Archive directories use mode `0700` and files use `0600`.
Content-aware scans found no private key, real token, JWT, credential URL, real hardcoded
password, or confirmed PII in the admitted bytes.

The archive-only preservation ref is
`codex/c3-archive-preservation-20260728` at
`6b2ef89da447353380b99853168d4d38aaf9210a`. Its sole parent is the fixed clean parent
above. Its visible path/mode/size/content manifest exactly matches the quarantined workspace;
that manifest SHA-256 is
`034c02786cc70034b6791a94f9d4222a1f69bdb0066171015a8e79f48dc01283`.
An independent read-only review reported `APPROVED`, with P0/P1/P2 all zero. The preservation
commit is not reachable from `master` or the active lean integration branch.

## Active lean integration

The active branch starts directly from the fixed clean parent and does not inherit the
preservation commit. It installs:

- a 36-line lean root governance file;
- durable domain and source/decision contracts;
- the exact 283-row frozen catalog;
- a lean coverage ledger and schema;
- a stateless deterministic coverage checker with focused tests;
- the approved C3.1 design and this report.

The frozen catalog SHA-256 is
`72c849825c9cbd39cb25f743d448b67a2a31bfccf7cfb68a3d2557c7bda178bf`.
It contains 197 Foundation rows and 86 deferred/full-only rows. The initial ledger contains:

| Initial disposition | Count |
| --- | ---: |
| `PENDING` | 106 |
| `HISTORICAL_PASS_CANDIDATE` | 85 |
| `WIP` | 6 |
| `DEFERRED_FULL_ONLY` | 86 |
| Total | 283 |

No historical receipt or archive checkpoint is treated as current integrated-tree
acceptance.

## Dirty-path disposition

`cutover-dirty-path-disposition.json` contains every quarantined visible dirty path exactly
once. Its sorted source-path manifest SHA-256 is
`f4baccb49ea2cd331c76aa9c3b41dc4a4952be7be22a1e03ebac2524b0d22ab0`.

| Disposition | Paths |
| --- | ---: |
| Archive-only history | 283 |
| Named product adoption stories | 189 |
| C3 governance/source adoption | 2 |
| Total | 474 |

Archive-only paths remain available on the preservation ref but never enter active ancestry.
The remaining 191 paths may enter only through their named reviewed adoption story. This
inventory is a preservation and routing proof, not a product PASS.

## Known preservation exception

`git diff --check` on the byte-exact archive checkpoint reports pre-existing Markdown
whitespace/end-of-file findings. Those bytes were intentionally preserved rather than
silently repaired. The active lean adoption must pass its own scoped `git diff --check`.

## Next gate

The governance adoption commit requires focused checker tests, inventory validation,
scoped lint/diff checks, and independent High review of the exact commit. Only after that
gate passes may the three product adoption canaries start.
