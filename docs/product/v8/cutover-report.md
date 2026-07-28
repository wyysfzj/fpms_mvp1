# FPMS C3.1 Lean Cutover Report

- Date: 2026-07-29
- Status: `TERMINAL PASS`; rolling product adoption is enabled
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

After the three canaries, the same 283-row ledger contains:

| Current disposition | Count |
| --- | ---: |
| `CURRENT_VERIFIED` | 17 |
| `SUPERSEDED_BY_STORY` | 5 |
| `PENDING` | 84 |
| `HISTORICAL_PASS_CANDIDATE` | 85 |
| `WIP` | 6 |
| `DEFERRED_FULL_ONLY` | 86 |
| Total | 283 |

`SUPERSEDED_BY_STORY` rows resolve only to reachable `CURRENT_VERIFIED` stories. Inventory
validation against the current integration `HEAD` passes.

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

## Governance review and canaries

Lean-governance adoption and the stateless checker correction each received independent
High review with zero P0, P1, or P2 findings. The three canaries are:

| Canary | Current reviewed commit/range | Decisive verification |
| --- | --- | --- |
| Schema spine | `38e3e6b` | 53 serialized schema/migration tests |
| Lifecycle evidence-kind adoption | `7bb54ce` | 190 serialized lifecycle/migration tests |
| Case-status UI vertical | `8640bca..dfd3ead` | 45 backend tests and 2 serialized Chromium tests |

Each canary has an exact story card, reachable Git scope, current-tree fingerprint,
independent `APPROVED` review, zero P0/P1/P2 findings, and explicit ledger mapping. Scoped
Ruff/diff checks passed for backend canaries; targeted ESLint/diff checks passed for the UI
vertical. No custom owner/scope scan, new taskctl state, canonical-scope artifact, or
per-task accept engine was used. Git scope/diff and the stateless inventory check complete
in seconds rather than minutes.

One UI reviewer lane exhibited a tool-level liveness failure before producing decisive
output. It was stopped at the bounded liveness threshold; durable commits and successful
checks were not repeated. A minimal independent command-only lane then produced the fresh
decisive results used by the approving reviewer. This is a runtime transport/tool issue,
not a product or governance-contract failure, and the Lean recovery rule handled it without
creating another governance subsystem.

## Cutover conclusion and next delivery gate

All C3.1 governance cutover completion conditions are satisfied: quarantine and archive
remain preserved; every original dirty path has one disposition; the active branch begins
from the fixed clean parent; Lean fail-closed domain/source rules are active; old
taskctl/evidence/scope machinery is read-only history; the governance bytes and all three
canaries have independent zero-finding acceptance; and no push, reset, clean, stash, or
user-change discard occurred.

This terminal cutover PASS does **not** claim the V8 product Goal is complete. Rolling
Git-native product story waves may now continue. Foundation, eligible Full, Final, and
Release remain pending and Release remains last.
