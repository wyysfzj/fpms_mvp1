# Independent Review — V8 Case Fee-Reduction Vertical Current Adoption

- Review class: `PROTECTED`
- Reviewed range:
  `89d2686db34e3ff419e3a93300da80e78aadc666..05e88ef32f4393a0161ca6e176dd0b47fc7dc3c6`
- Reviewer: independent GPT-5.6 High review lane
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The exact eleven-path story implements catalog rows 98–100 without absorbing the pending
CaseEdit fee-reduction UI. Create and update accept only canonical string ratios `"0"`,
`"0.7"` and `"0.85"`; malformed, numeric, blank and symbolic alternatives fail request
validation. Ratio `"0"` performs no approval lookup. Reduced ratios require one current
confirmed approval whose applicant combination, fee scope and effective scope match
exactly; ambiguous valid approvals fail deterministically with 409.

The create and update services validate fee reduction before status, case or child-table
writes. Applicant-combination changes require an explicit replacement selection. The UI
starts unset, exposes Simplified Chinese required choices and sends only canonical ratios.
No official rate, source activation, applicant policy or customer decision is inferred.

Fresh independent verification:

- backend five-file tranche: 98 passed, 19 subtests passed;
- Chromium Playwright exact three-spec tranche: 5 passed;
- scoped Ruff, exact-file ESLint, exact-story `vue-tsc --noEmit` and diff-check: passed;
- reviewer content-manifest SHA-256:
  `b307d54ab3df20b80995bb12f87d83b1cc0b5ceeefb659f9730bfb1a98fa211f`;
- Lean exact Git path/mode/blob fingerprint:
  `63231a6b9dd4a22c1a7e860ff04fe4e28fdcf65bc9d7e1df2666788a9bdd0153`;
- patch SHA-256:
  `bd6056abfaa48f54792328407db0a959893e2d23d8f93abbdf333033695b8f34`;
- story SHA-256:
  `c3ec76eab81a7f8110c569d7c199b37682a5e6bcd9545f85f5e886b7f6c341a0`.

The existing case-status UI vertical was independently re-attested compositionally. Its
lifecycle behavior remains unchanged; overlapping fixture changes only make the new
required fee-reduction selection explicit. Its current tree SHA-256 is
`6ed8e9c3b8325cdf0234986767a9080dcc1b480a451abf24f8254daf37de2dbf`.
