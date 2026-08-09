# Independent Review — V8 Document Create Lifecycle-Neutral Successor Contract

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/row61_successor_contract_review`
- Exact candidate commit: `d754b8c265133459af19a2ceb48f99f20bb07985`
- Inspection base: `ff4308e26016e714f09f39221d5a7f1ad2be7447`
- Story:
  `docs/product/v8/stories/V8-DOCUMENT-CREATE-LIFECYCLE-NEUTRAL-SUCCESSOR-CONTRACT.md`
- Integration binding: `UNBOUND` (the controller owns implementation and later
  coverage-ledger binding)
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The corrected contract closes both findings from the initial review. It no longer claims
that acceptance/OA evidence adapters already exist: it accurately records that the current
tree contains only their accepted pure lifecycle rules and freezes two exact dedicated
`Doc.Edit` routes with authenticated actor ownership, strict request shapes, caller-owned
commit/rollback and HTTP 200 responses. Ordinary single create, wizard/batch create and
ordinary edit remain lifecycle-neutral and cannot dispatch the computed routing metadata.

Both new adapters fail closed around exact inbound executable template semantics, one
current final independently approved `OFFICIAL_FINAL_PDF` evidence version, canonical
stored identity/hash/review facts and one confirmed lifecycle event. The OA adapter also
requires the exact confirmed official-deadline tuple and the frozen case-sensitive
template-code-to-sequence mapping. Client input cannot supply legal/event/evidence truth;
exact replay is idempotent and bound-fact drift remains a lifecycle conflict.

The archive commit `6b2ef89da447353380b99853168d4d38aaf9210a` is explicitly implementation input only,
not acceptance authority. The current domain contract, source-decision record, accepted
lifecycle rules and this independently reviewed successor contract remain authoritative.
The source SHA-256
`91a336042550c2ee616f43654f4216955f6fff774528b696c676faebb4f1ac64` exactly matches the
UTF-8 decision text `批准方案 A，Resume Goal`.

The verification contract now names the three decisive successor tests, the four narrowly
alignable obsolete-assertion files and all sixteen accepted shared-seam regression files.
No other test assertion may be changed to manufacture GREEN. Dedicated evidence adapters,
deadline/reply/task/fee behavior, grant ownership, schemas, permissions, public existing
shapes and historical evidence remain outside the mutation boundary.

Exact review identities:

- cumulative two-file binary patch SHA-256:
  `a7f9c9007ef141d7cdf4ec14ec16c5536f89d3a9e57d9ce6e5dc2c71e22dead0`;
- story SHA-256:
  `351f35f5171e060d7e01f69de18822be8b2f4d789542dcaa36afc5ce986e72e7`;
- registry Git blob: `d87967c5a254bd59563c9f7b07f971f73b375d19`;
- story Git blob: `3bc0de89126eadd34b22987306b9b84c1b43a3cc`.

This receipt approves only the exact frozen contract candidate. It does not approve an
implementation, activate ordinal 61 in the ledger, adopt archive product bytes or claim a
Foundation/release milestone.
