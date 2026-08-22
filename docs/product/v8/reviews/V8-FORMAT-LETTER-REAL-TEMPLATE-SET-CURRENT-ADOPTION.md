# Independent Review — Format Letter Real Template Set Current Adoption

- Review class: `PROTECTED`
- Reviewer: independent High reviewer `/root/row88_independent_review`
- Candidate commit: `47e65e1eb192226ffc411728bf123644da2ff45d`
- Inspection base: `4af1414b24ee96e11c793fc2e2dec524dfa0d7ee`
- Historical comparison anchor: `83d014fb825c76e90c53821c7db9ed7f3cd49436`
- Story: `docs/product/v8/stories/V8-FORMAT-LETTER-REAL-TEMPLATE-SET-CURRENT-ADOPTION.md`
- Integration binding: `UNBOUND` (the controller owns the later coverage-ledger binding)
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The independent High review verified the exact frozen row-88 closure: one immutable
eight-entry dataset, `FPMS-FORMAT-LETTER-CUSTOMER-20260610-V1`, with stable codes
`FORMAT_LETTER_001` through `_008`, exact customer-source hashes, template-version IDs,
mapping patterns, output paths, provenance fields and undeclared-variable sets. The eight
committed DOCX packages preserve the frozen A4-landscape customer structures and exact
semantic placements, render without unresolved Jinja or merge markers, and retain the
special three-variant single-row behavior for template `007`.

The seed validates the complete dataset before mutation, fails closed for missing,
invalid, placeholder, wrong-variable and ambiguous carriers, updates eligible legacy rows
in place, preserves caller-owned transaction semantics and unrelated/manual rows, and is
idempotent after the exact eight Templates and mappings exist. The prerequisite
`FPMS-V8-DE-REGISTER-VERSION-20260712-01` is `CURRENT_VERIFIED` through
`V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION`.

## Exact current-tree and historical identity

Candidate `47e65e1^..47e65e1` adds only the story card; it changes no product, test,
template, ledger or historical task/evidence byte. The focused test and all eight template
blobs are byte-identical to anchor `83d014f`:

- focused test: `8c18682a8c155198e2ecc8cc1acca58504b0d242`;
- templates `001` through `008`, respectively:
  `202e54400c72a491c5bad53198e9e5a9a87a8c0c`,
  `b7eb23d501381dd08cb3c9b9074f6b81e3af6b25`,
  `68425f12984c66ad2906c33231f498836955ecf0`,
  `8e29a5ef2764a5c77bb4bec6f82945b74b17616b`,
  `a6c531311e5dae70e45cf15617e0542d7278edca`,
  `eaa2b686f10bb766285f46245c4457d18af40f62`,
  `ad59c2587ff866c866d22fcebf051adc4082315b` and
  `37322aa4054b8818271f7e8629b626179aa9bd1c`.

The complete current seed blob is
`30d275d1677071fcbd4ac534ad5d7d1d57bd5196`; anchor `83d014f` has
`82a58ec0035cb97116a4303f9d14e956972ac841`. Their row-88 catalog, validation and seed
slice has the identical SHA-256
`7abe35c2ba22df5781d071a2ac0d8895bb6da3e5ceb5c1118a4f4f0f1a455f98`.
The only complete-file difference is the two import/call lines successively owned by
`36ab390` application-fee-notice activation and `caf0da6` fee-reduction-approval-notice
activation; both are outside the row-88 hunk and leave its call and behavior intact.

The exact ten-path current Git-tree fingerprint is
`2e18cd2b91f97f14e4f4dd1a0da0392e47f119f5eeb261d08c0bac5cbdf26620`.
The story-card SHA-256 is
`74d35f4b6ae7331d55a8f541e3cdbd3cc4140cdddb6b11bdddb81bf5b50c492f`,
and its exact candidate binary-patch SHA-256 is
`cd5d92e571fb7bfda12b0def842e7b4f46152838d259acf33fd8b4ce13eed170`.

## Fresh independent verification

- From `backend`, `PYTHONPATH=. python3 -m pytest -q
  tests/test_v8_format_letter_real_template_set.py` returned `14 passed, 1 warning in
  7.97s`, exit `0`. The warning is the inherited passlib `crypt` deprecation. The
  serialized SQLite lane was released immediately afterward.
- `git show --check 47e65e1` returned clean, exit `0`.
- Exact candidate scope is the single story-card addition. The ten row-owned product/test
  paths plus story have no worktree drift from `47e65e1`, exit `0`.

No ninth mapping, second dataset, new customer wording, API/UI/schema/migration, context,
renderer/archive/email behavior, calculation rule, fallback, customer-decision activation,
adjacent seed cleanup, ledger/story/task/evidence mutation or Foundation/release claim was
absorbed.
