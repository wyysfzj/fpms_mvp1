# Independent Review — V8 CNIPA 246 Layout Rate Candidate

- Review class: `PROTECTED`
- Exact integration range:
  `60c35213c67218ff4c2f1664bbdc832e3f976a6c..82bc4f7ac2507b1eef740d538baf60797b3e7559`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The implementation captured the public-interface RED before product bytes existed:
`17 failed`, with the decisive missing-materializer signal. After the exact canonical
data and materializer adoption, the focused GREEN returned `17 passed, 1 warning in
4.94s`. The independent reviewer reran the exact focused SQLite test once:
`17 passed, 1 warning in 4.73s`, then released the serialized slot. The warning is the
inherited third-party passlib `crypt` deprecation.

The independent High review confirmed the exact frozen graph:

- one `CNIPA_LAYOUT_246` book, version and effective start `2017-07-01`, no effective end;
- `PENDING/INACTIVE` book with null approval, activation and current identity;
- one linked `IC_LAYOUT_REGISTRATION_FEE=1000.00 CNY` rate;
- `GOV/FIXED`, reduction disabled, enabled, `PENDING_CONFIRMATION`;
- exact canonical-data, normalized-source, provenance and source-snapshot hashes;
- exact replay with stable identities and zero mutation;
- deterministic 409 on changed replay;
- caller-owned commit/rollback and savepoint-only failure rollback; and
- no activation, promotion, seed, fallback or runtime consumption.

The exact five-path range contains only the materializer, canonical JSON, focused test,
the two/count disposition correction and story card. The three product/test paths move
from `V8-ADOPT-ANNUITY-RATE-SOURCES` to this story, changing the former count from 34 to
31 and adding the new owner with count 3. All 474 disposition entries remain unique and
reconcile. The accepted source files and registry remain unchanged.

Scoped Ruff, exact diff-check, inventory, archive identity and clean-status checks passed.
The binary patch SHA-256 is
`8b27b186bb5e739e8c48237f978d7d18283baf4298b5b9b7b96566afe213bcab`.
The exact three product/test path Git tree fingerprint under the C3 checker algorithm is
`dbd0a7467b0ebd301df17ae41c6a1c3892f15a0e986d4b5f1c6498d211dfb96f`.
