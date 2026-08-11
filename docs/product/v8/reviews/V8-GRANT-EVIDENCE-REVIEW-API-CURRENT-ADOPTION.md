# Independent Review — Grant Evidence Review API

- Review class: `PROTECTED`.
- Product commits: `9da9f082ace6b471c87581269d92be2a498a3cf9`,
  `db885f28ff814e6b2e49cd413448248123f15dbe` and
  `771b5eeb210cefb6cefb6f0d716c6475dbc43555`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact POST endpoint `/documents/grant-evidence-candidates/{candidate_id}/review` requires
`Doc.Edit`, derives the reviewer and review time on the server, delegates proposer/reviewer
separation, source/role validation, compare-and-swap review and accepted dispatch to the existing
service, preserves its error envelope, and owns the outer commit/rollback boundary.

Independent review found and closed two P1 defects. A real missing candidate now receives typed
`GRANT_EVIDENCE_REVIEW_NOT_FOUND`/404 from the service without a duplicate API lookup, while all
corrupt, role, source, replay, CAS and dispatch conflicts remain 409/no write. Its new visible
message is Simplified Chinese. Route, schemas, permission, server-owned fields, dispatch and
transaction behavior remain unchanged.

Fresh verification passed the complete focused service/API suites (`33 passed`), scoped Ruff and
the exact cumulative diff check. Final independent High review approved with zero findings. The
relevant-path cumulative patch SHA-256 is
`cbb811ab9ee1aaf2e4e5ac94d7e00c03124c6b191334a23d40487e1265003b77`; its exact six-path
Git tree fingerprint is
`0318378dd263b73837aa81de664ca0d0c01f9ea5ca26c08900acf5e0dddc1e83`.
