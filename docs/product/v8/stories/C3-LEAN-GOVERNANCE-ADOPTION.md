# Story C3-LEAN-GOVERNANCE-ADOPTION

- Risk: `PROTECTED`
- Outcome: replace the legacy taskctl/scope/evidence control plane for new work with the
  approved Git-native C3.1 delivery rules while retaining every FPMS fail-closed invariant.
- Authority:
  `docs/superpowers/specs/2026-07-28-fpms-c3-git-native-lean-56-reset-design.md`
  §0, §6, §8, §9.6, §12 and §18.
- Catalog IDs: none; this is the one-time governance cutover prerequisite.
- Dependencies:
  archive-only checkpoint `6b2ef89da447353380b99853168d4d38aaf9210a`;
  active branch parent `afa58429e6b6e80b85f76055139e18fbe38ec9e8`.

## Closure

- Install the lean root rules.
- Migrate domain safety and source/customer authority to tracked product contracts.
- Track the exact frozen 283-row catalog.
- Define the coverage-ledger contract and a stateless deterministic checker.
- Give every one of the 474 quarantined visible dirty paths one exact disposition.
- Record the archive, isolation, safety-scan and cutover facts without claiming product
  acceptance.
- Preserve the approved C3.1 design in the active integration branch.

## Non-goals

- No product code or product task adoption.
- No historical taskctl state mutation or false PASS.
- No owner, lease, event, candidate, scope, controller or compatibility service.
- No Foundation, Full, Final or Release claim.

## Owned paths

- `AGENTS.md`
- `docs/postdemo/postdemo_application_fee_notice_preview_source_decision_20260721.md`
- `docs/superpowers/specs/2026-07-28-fpms-c3-git-native-lean-56-reset-design.md`
- `docs/product/v8/**`
- `scripts/v8_lean_coverage_check.py`
- `scripts/tests/test_v8_lean_coverage_check.py`

## Verification

- Checker RED before implementation and focused GREEN after implementation.
- Exact catalog SHA-256.
- Inventory validation for the initial 283-row ledger.
- Scoped Python lint and `git diff --check`.
- Independent High review of the exact adoption commit.

## Rollback

Abandon the active lean branch and return to fixed clean HEAD. The original quarantine,
external evidence archive and archive-only checkpoint remain unchanged.
