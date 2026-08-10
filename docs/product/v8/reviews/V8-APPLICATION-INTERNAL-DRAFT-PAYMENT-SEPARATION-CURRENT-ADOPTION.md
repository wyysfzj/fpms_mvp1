# Independent Review — Application Internal-draft and Payment Separation

- Review class: `PROTECTED`.
- Reviewed range:
  `7955b90bf5fb9fd6355fcf07337e45422d597572..3f34b3e96d6509c478a27ae5973a1c5323243a93`.
- Task SHA-256:
  `2a04bd220a0d1c96b61b5d7bb027add302cb55fc1ba69575b8724503215a9937`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact eight-path candidate implements Scheme A's application-fee boundary: a current,
source-backed reviewed real notice may create one reusable internal draft while customer
instruction remains `PENDING`; no PayList, GovPayment, payment evidence or inferred `PAY` is
created. The unchanged payment path becomes eligible only after an explicit customer `PAY`.

The corrected candidate begins the real SQLite outer transaction before decision-gate resolution,
validates the exact persisted review, recognition, evidence, current-line, actor and idempotency
lineage, rejects `SOURCE_PENDING` and corrupt graphs, and preserves exact read-only replay after
later payment/evidence state. It adds no API/router/runtime trigger, schema, migration, grant-year
or future-annuity behavior.

Fresh independent verification passed: canonical focused pytest `53 passed`, exact ten-file
affected regression pytest `198 passed`, scoped Ruff check-only passed, and the exact cumulative
eight-path diff check passed. The exact eight-path Git tree fingerprint is
`038fe698309ef53823ffe8b462fa65874d5ebe90847d4bd511963857cb3230e4`.
