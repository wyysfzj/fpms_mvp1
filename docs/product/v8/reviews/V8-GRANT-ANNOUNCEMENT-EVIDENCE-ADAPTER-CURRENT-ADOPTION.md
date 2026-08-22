# Independent Review — Grant Announcement Evidence Adapter

- Review class: `PROTECTED`.
- Frozen task commit: `c176e6720807d7ca1d5a04f64999ff830959e5ce`.
- Implementation commit: `5c228a308c50195fc255572b1712a92ca6ab0273`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact two-path adapter accepts only a canonical, hash-bound, unconflicted
`GRANT_ANNOUNCEMENT` candidate with an `APPROVED` second-person review. It resolves and matches the
source authority at review time, the proposal authority and membership at proposal time, and the
review authority and membership at review time. Missing, stale or mismatched authority fails with
`GRANT_ANNOUNCEMENT_EVIDENCE_CONFLICT` / 409 before lifecycle dispatch.

Exactly one canonical `announcement_date` is mapped to one
`GRANT_ANNOUNCEMENT_CONFIRMED` command. The event binds the evidence version and content hash,
candidate provenance, canonical source snapshot, persisted proposer/reviewer and deterministic
idempotency key. It delegates once to the accepted lifecycle service, which owns exact replay.
The adapter performs no candidate query/mutation, direct case-status write, flush, commit,
rollback or transaction close. Private reuse of the accepted review service's side-effect-free
candidate validator was independently checked and introduces no behavioral boundary violation.

Fresh verification passed: focused adapter pytest `6 passed`; direct-status, lifecycle rule and
review-service regressions `97 passed`; all focused consumers of `evidence_policy.py` passed
`522 tests and 6 subtests`; scoped Ruff and exact two-path diff check passed. The exact two-path
Git tree fingerprint is
`2441b23eb7ceb5fdbbd1fba01cb78fe794d351dccbd33cd015fb516124d7cd90`.
