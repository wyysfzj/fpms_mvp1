# Independent Review — V8 Annuity Payable-Amount Rule

- Review class: `PROTECTED`
- Exact integration range:
  `21b12ae9dc740f19686584978acbd2e22555dd06..def9414f585466c6c8907230a7f5d5b0fce24ed9`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

Both independent review axes confirmed that the exact range adds only the 99-line story
card and changes no product, test, persistence, source, registry, ledger, disposition,
API, UI, schema, activation or runtime byte.

The independent reviewer reran the exact payable-amount test together with its
first-ten-year reduction dependency regression: `62 passed, 1 warning`. Scoped Ruff and
exact story-only diff-check passed and the worktree was clean. The warning is the
inherited third-party passlib `crypt` deprecation.

Static and runtime verification confirmed exact finite positive `Decimal` validation,
full-fee error precedence, one final two-place `ROUND_HALF_UP` quantization independent
of caller precision, immutable result values, and `late_fee_base` equal to the unreduced
full annual fee. The rule performs no persistence, I/O, clock read, source selection,
approval, activation or obligation/payment write.

The focused test remains archive-identical at blob
`270a3c859bf440b3aad2753bb9baf96eb66d1659` and SHA-256
`ac8e01e827f5c1eebe07eb6be683ac0a35087b909feb4efd69ff457403899213`.
The current and archive constants/result/function slice SHA-256 is
`087d941aef7f7e45652da9cf8ef168f479020adc6814e934f2cef56afeccf4fd`.

The full binary patch SHA-256 is
`20f105385e8bea3671879479722cb977115d62f094f5186a73c354ed05fd5058`.
The exact product/focused-test Git tree fingerprint under the C3 checker algorithm is
`6ac44d3db8583507822a4241ed947da984c82804d9f38d65feb8e145469a9b43`.
