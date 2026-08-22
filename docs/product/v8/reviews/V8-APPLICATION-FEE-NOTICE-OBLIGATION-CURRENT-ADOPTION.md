# Independent Review — Application-Fee Notice Obligation

- Review class: `PROTECTED`
- Product commit: `e307d68`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The current story adopts the archive-owned application-fee notice carrier and freezes the
`APPLICATION_FEE_NOTICE` semantic. It recognizes or reuses an obligation only from an
exact canonical notice with confirmed due/source/item authority. Preview differences enter
`REVIEW_REQUIRED`; no activation or draft is created.

The first review found two P1 authority gaps. The final candidate now accepts only
`MANUAL_OFFICIAL_NOTICE` or `IMPORTED_OFFICIAL_NOTICE`, includes that source in replay
identity, and binds the supplied evidence to exact current, final, approved same-case and
source-document truth. It also validates the reviewer/time plus canonical confirmed review
activity payload and evidence reference. Unrelated or mutated review graphs fail `409`
before recognition.

For PCT notices, the carrier entry date maps only to current policy `effective_on`.
Exemptions require mirrored confirmed RO/search/report evidence; `pct_policy.py` is
unchanged and no `case_type` inference occurs. Caller transaction ownership and the
no-activity/task/reply/status side-effect boundary remain intact.

Final focused GREEN passed `26/26`; scoped Ruff, compile and diff checks passed.
Independent High re-review matched all exact hashes and approved P0/P1/P2 all zero.

The exact product/test tree fingerprint is
`44378ecefbc2673037a16f2d26486db761531c224c07844c5da4a59b5376dbf1`.
The complete product commit patch SHA-256 is
`774af51823d2359e9f73ceb8f9a24cd38c056f13a6bf6abddb654d90fdebc0a8`.
