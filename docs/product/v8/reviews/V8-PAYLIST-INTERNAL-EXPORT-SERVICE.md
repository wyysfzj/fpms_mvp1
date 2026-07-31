# Independent Review — V8 PayList Internal Export Service

## Exact reviewed range

- Base: `89d2686db34e3ff419e3a93300da80e78aadc666`
- Story commit: `f89e67e60db95ce34046acc84aaafd53703f3fea`
- Exact patch SHA-256:
  `bc7624669b92c016de16e836788e2155ff725a3fa7d2197a79b314de4a0f6c71`
- Story SHA-256:
  `3e40f5632f720e36b8752055a7062c66c7a33f54a845f94a18f4ece3062e745c`

## Row 160 verdict

Verdict: APPROVED

- P0: 0
- P1: 0
- P2: 0

The independent High reviewer verified the exact three-path range. The focused test is
byte-identical to archive blob `7322dd5f7081ae8102a6831bfd506a0de3d4c90a`;
`export_excel.py` remains unchanged at blob
`beafa9b6ad228a26947e3bbd321fe9c2a7b63a0f`; and the adopted service slice has SHA-256
`ce2a221b6b03ec61592a55f3c76211c0e250aee96d2a61e1be9de6bd96957c3a`.

The reviewer confirmed deterministic workbook bytes and hash, managed artifact lineage,
exact replay, conflict/missing/symlink/path/hash/activity and partial-write fail-closed
behavior, caller-owned transaction semantics, and no official-upload, payment-status or
official-evidence claim.

## Shared-service successor re-attestation

`V8-OFFICIAL-PAYMENT-EVIDENCE-ACTIVITY`

- Verdict: COMPOSITIONAL SUCCESSOR RE-ATTESTED / APPROVED
- P0: 0
- P1: 0
- P2: 0
- Current tree SHA-256:
  `61e7c269b38c4ca65c012213363f7b0e800cfced2cbce5fbb94aa6d8dd8ca019`

`V8-ACTIVITY-ADAPTERS-CURRENT-ADOPTION`

- Verdict: COMPOSITIONAL SUCCESSOR RE-ATTESTED / APPROVED
- P0: 0
- P1: 0
- P2: 0
- Current tree SHA-256:
  `095a1ac160fdf66cfa168543fdcf3fb17357a46fc0d083f1639115f547d9ee5b`

The only later change to their shared `annuity/service.py` is the independently reviewed
row-160 slice. Their story cards and focused tests remain unchanged, and their official
payment evidence and activity-adapter semantics remain intact.

## Fresh verification

- Row 160 + row 159 carrier + row 124 + row 125: `19 passed` in 7.54 seconds.
- Scoped Ruff across the ten relevant Python paths: passed.
- Exact range, carrier dependency and both successor ranges:
  `git diff --check` passed.
- The only warning is the existing third-party `passlib` use of Python `crypt`.
- Reviewer made no file changes; the reviewed worktree was clean.

Task 133 successor commit `807c93e0d389e05f4c620c287d8eed17a74b2f83` adds a
disjoint Future Annuity seam to the shared service. The exact six-consumer successor
tranche passed `26/26`; independent Task 133 review approved P0/P1/P2 `0/0/0`. The current
three-path fingerprint is
`27625147a48b612015b640396a98a203b9481b22272073b26ad3b8e130333ad1`.
