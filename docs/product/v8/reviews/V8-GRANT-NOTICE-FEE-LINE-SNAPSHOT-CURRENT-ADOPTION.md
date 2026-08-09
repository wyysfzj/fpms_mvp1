# Independent Review — Grant Notice Fee-Line Snapshot Current Adoption

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/row67_independent_review`
- Candidate/current commit: `2b212aeaaec5c5bc1514d7fcd34a454b35d6f211`
- Inspection base: `89fa7e1a962aee9aacc3e2acd2831c823e8b45c4`
- Historical product/test anchor: `83d014fb825c76e90c53821c7db9ed7f3cd49436`
- Story:
  `docs/product/v8/stories/V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-CURRENT-ADOPTION.md`
- Integration binding: `UNBOUND` (the controller owns the later coverage-ledger binding)
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

## Independent contract and boundary review

The reviewed current bytes implement exactly one frozen, keyword-only public parser and
two immutable slotted DTOs. The parser reads only the supplied `Document.id` and
`Document.extra_data`, binds the exact reviewed evidence-version identity and lowercase
prefixed evidence hash, preserves fee-line order, and emits only the exact canonical
`FPMS_GRANT_NOTICE_FEE_LINES_V1` JSON plus its bare lowercase SHA-256.

Validation follows the frozen order and fails closed for wrong bindings, malformed or
non-object JSON, duplicate keys at any nesting level, non-finite tokens, missing or empty
`GrantFeeLines`, wrong line fields/types, invalid names, non-positive or duplicate years,
invalid decimal spellings/scales and ratios outside exact strings `0`, `0.7` and `0.85`.
Accepted amount spellings alone normalize to two decimal places; top-level siblings are
ignored and ordered facts are not trimmed, inferred or sorted.

The callable has no `Session`, repository, service class, second callable, SQL, mutation,
file/OCR/PDF access, clock access, rate or eligibility lookup, obligation/draft/task
creation, lifecycle activity or downstream write. It deliberately does not decide
current/FINAL/APPROVED evidence state; the contracted successor adapter owns that check.
The review-service prerequisite
`FPMS-V8-DE-REVIEW-SERVICE-20260712-01` is `CURRENT_VERIFIED` through
`V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION`.

## Exact candidate, anchor and current identities

Candidate `89fa7e1..2b212ae` adds only the 45-line adoption story. It changes no product,
test, task, ledger or historical evidence byte. The two current paths are byte-identical
to anchor `83d014f`:

- source Git blob at anchor and current:
  `e27a994f26aa48cae01cffd216220cc690d8e291`;
- test Git blob at anchor and current:
  `aabda6a78306a3ad81cb771e29cdf494bd26e8e3`;
- source SHA-256 at anchor and current:
  `543e13c68321ce6457c71d30a3421b8938e4bf5f4b923b38c58b334db4545305`;
- test SHA-256 at anchor and current:
  `47c63ca09e25060267c058453bf01055d4d269ffa71400e7fe2e713d3f1b0a30`;
- story Git blob: `49fd6af31513000904d3ecb56b6de5f997346267`;
- story SHA-256:
  `45ad5b7fc51f8cd997636c908f8ab3d3bd05282ff39feaba08b8c5b444bed36d`;
- exact three-path current Git-tree fingerprint:
  `e2f334b670f8b57203cd3a22966d4b31ae622954efb68c16ca646ef366a1158f`;
- exact two-path anchor Git-tree fingerprint:
  `100281da204c8f583b37501b69271ae9efb6815b5d7d38644da86cdc5f27ce73`;
- candidate binary-patch SHA-256:
  `9c6b4ab931902c30bcec763f2563f8cb1d8897364099f570f28bcad16564b986`.

## Fresh independent verification

- From `backend`, the exact focused command
  `pytest -q tests/test_v8_grant_notice_fee_line_snapshot.py` returned
  `46 passed, 1 warning in 11.62s`, exit `0`. The warning is the inherited passlib
  `crypt` deprecation; the serialized SQLite lane was released immediately afterward.
- Scoped `ruff check` on the source and focused test returned `All checks passed!`, exit
  `0`; its only message was the repository's existing top-level-settings deprecation.
- `git diff 83d014f 2b212ae` on the source/test pair was empty.
- Exact anchor/current and candidate-story `git diff --check` commands returned exit `0`.
- The worktree was clean before receipt creation.

No parser change, second seam, evidence-state decision, grant lifecycle adapter, fee
amount/rate or reduction-eligibility rule, obligation/draft/task behavior, API/UI,
schema/migration, OCR/PDF, file access, ledger mutation or Foundation/release claim is
approved or absorbed by this receipt.
