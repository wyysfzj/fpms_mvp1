# Independent Review — V8 Fee-Obligation HTTP/FE Vertical Current Adoption

- Review class: `PROTECTED`
- Reviewed range:
  `08fd297bce682f3011b30add1918354db4e6d896..446d295fd860bda3bfee2466da0a222f7aa8ff6b`
- Reviewer: independent GPT-5.6 High review lane
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The exact nine-path range binds catalog rows 108, 109, 111 and 112 to one observable
backend/frontend vertical. The instruction endpoint preserves `Fee.Edit`, server-owned
actor identity, direct replay facts and caller-owned transaction semantics. The bodyless
detail endpoint preserves `Fee.Read`, one-call read delegation, separated persisted states,
decimal/date strings, line/source identity and zero transaction action. The frontend
adapters return the direct server representations without inference.

The reviewer approved the predecessor alignment required by the new GET successor: no exact
collection POST route exists; the dynamic GET successor makes the collection-shaped POST
return 405 with `Allow: GET`; the legacy body-ID POST remains 404; neither invokes the
service or transaction.

Fresh independent verification:

- serialized six-file backend tranche: 168 passed in 55.82 seconds;
- scoped Ruff, Ruff format-check and exact-range diff-check: passed;
- both exact isolated TypeScript contract probes and exact-file ESLint: passed;
- candidate and fresh base typechecks produced the same seven inherited errors and zero
  owned-path errors;
- the three CaseEdit fee-reduction/status Chromium specs, serialized with one worker:
  5 passed in 21.4 seconds;
- exact eight product/test path Git fingerprint:
  `cd9a24ee83d1a53ef8d01e182ebf9b6cd98ce1d0da19a928fb4568fb10b4df9b`;
- patch SHA-256:
  `c7b92802d6b2b1a57f76aebf9cbbf42a98c5eb70cf33079b58b7063f12293815`;
- story SHA-256:
  `509f516ba255ee8181e8e4cd7c08b480c1962a4cadebb3e97f5d17f2ffbf142a`.

The shared CaseEdit fee-reduction and fee-reduction approval API stories were independently
re-attested. No row 113/114/116, page behavior, schema/migration, fee policy, draft,
payment/evidence or lifecycle behavior was absorbed. All dedicated processes, dependency
links, browser output and baseline exports were removed; the reviewed worktree was clean.
