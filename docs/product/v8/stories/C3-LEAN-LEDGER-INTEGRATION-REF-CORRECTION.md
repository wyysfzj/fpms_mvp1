# Story C3-LEAN-LEDGER-INTEGRATION-REF-CORRECTION

- Risk: `PROTECTED`
- Outcome: permit the stateless checker to validate the explicitly supplied current
  integration commit without requiring the ledger commit to contain its own future SHA.
- Non-goals: no owner/state/controller service, no reachability weakening, no acceptance
  without current tests/review, and no product or catalog disposition change.
- Authority: C3.1 §0 rules 7, 11, 17 and 18; §8.3 stateless checker contract.

## Exact contract

- `integration_sha: null` means the caller must supply `--integration-sha` (or the
  non-inventory CLI defaults it to `HEAD`).
- A non-null recorded integration SHA must still equal the resolved supplied SHA.
- Every `CURRENT_VERIFIED` story commit must remain reachable from that resolved SHA.
- Reviewed and integrated story tree fingerprints must remain exact.

## Verification

- Saved focused RED proves the former self-reference failure.
- Focused GREEN plus all checker tests and scoped Ruff.
- Inventory checker and full-range `git diff --check`.
- Independent High review of the exact correction commit.
