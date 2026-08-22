# Contract — C3 Lean Successor Path Attestation

- Risk: `PROTECTED`
- Trigger: the first Foundation milestone check after normal story integration rejected a
  previously reviewed story because a later reviewed successor intentionally changed one
  shared path. The current checker treats every historical story snapshot as the final
  integrated tree, which is impossible for the accepted shared-file delivery model.
- Outcome: retain immutable review proof for every story commit while attesting the current
  integrated bytes against the unique latest accepted owner of each tracked path.

## Exact contract

1. Every `CURRENT_VERIFIED` story keeps its existing requirements: nonempty commits, paths
   and tests; valid review class and receipts; every commit reachable from the declared
   integration SHA; and the recorded whole-story tree fingerprint exactly matching the
   story's final reviewed commit.
2. For each path named by one or more current-verified stories, the checker finds the unique
   latest accepted owner by Git ancestry of the stories' final commits. A later owner is a
   valid successor only when the earlier final commit is its ancestor.
3. The path bytes and Git metadata at the integration SHA must exactly match that unique
   latest accepted owner's reviewed commit. An unreviewed later edit therefore still fails
   closed. Earlier reviewed snapshots remain immutable historical proof and are not falsely
   required to equal the later successor bytes.
4. Incomparable latest owners, an absent path, an unreachable commit, a wrong recorded
   fingerprint or current bytes that differ from the latest accepted owner fail closed.
   Same-commit co-owners are permitted only because they resolve to the same Git entry.
5. The correction does not change catalog dispositions, review requirements, reachability,
   milestone eligibility, dirty-path quarantine, product behavior or release ordering.

## Exact paths and verification

- `scripts/v8_lean_coverage_check.py`
- `scripts/tests/test_v8_lean_coverage_check.py`
- this contract and later independent adoption/review records

Focused tests must prove accepted linear successor replacement, rejection of unreviewed
post-successor drift, and preservation of the existing single-owner/reachability/tree
failures. The current repository inventory and Foundation preflight are rerun after the
separately reviewed current source-registry authority is represented in the ledger.
