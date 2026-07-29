# Independent Review — Document Evidence Core Current Verification

- Review class: `PROTECTED`
- Exact commit: `6672d239e4f0aa7c0575ad5392987ef954140f0f`
- Parent: `d39813d4b678bb7bb9f5a6747165c77ec2d478af`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The Spec axis confirmed that rows 43–47 form one coherent serialized document-evidence
service core: immutable version and derivation registration, current-version switching,
irreversible independent review, and external-submission finalization. The row-42
contracts and lifecycle append seam are current, reachable prerequisites. Later OA-reply,
role-policy, API/UI, schema, lifecycle-transition, receipt and correction behavior remain
outside the story.

The independent Spec reviewer reran the exact seven-file serialized tranche: 164 tests
passed with one unrelated dependency warning. Nine-path scoped Ruff and exact diff-check
passed.

The Standards axis confirmed the range adds only the 87-line story card and leaves both
product and all seven test paths byte-unchanged. The story records the exact protected
outcome, authority, dependencies, paths, tests, exclusions and story-only rollback while
preserving twelve evidence roles, seven derivation types, and the explicit exclusion of
`OA_REPLY_PREPARATION` and `prepare_oa_reply`.
