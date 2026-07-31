# Independent Review — V8 Lifecycle Evidence API Adapters

- Review class: `PROTECTED`
- Full exact range:
  `e8e2388bdfb062f746556885e5f09767e1793163..13a40c33bdbb4eb89909284e088786f4232833f5`
- Fix range:
  `4c9f151a9951da68e23ae55402d442bc7b4830e1..13a40c33bdbb4eb89909284e088786f4232833f5`
- Verdict: `APPROVED`
- P0: 0
- P1: 0
- P2: 0

The story exposes exactly ten permission-protected document-evidence endpoints for frozen
catalog ordinals 78–87. Each endpoint resolves explicit typed, current, final and
independently approved evidence, delegates one named lifecycle event and preserves the
caller transaction. Acceptance notice, OA notice, certificate, generic lifecycle,
frontend, schema and migration behavior are excluded.

The initial independent review rejected the candidate because both evidence validators
accepted non-positive evidence version numbers and the rectification validator did not
validate the persisted attachment identifier. The reviewed fix requires an exact
non-boolean positive integer version in both validators and a canonical stored attachment
ID for rectification. Public HTTP regressions prove deterministic `409` and no lifecycle
activity or revision for each corrupt carrier. No API, router, permission, schema or model
surface changed in the fix.

The independent re-review ran the exact ten focused files plus the deadline-carrier
regression once: `313 passed, 3 warnings in 138.07s`. The warnings were inherited
deprecations. Scoped Ruff, full/fix diff-check and worktree cleanliness passed. Five
retained historical test blobs remain archive-identical; the rectification divergence is
the required fail-closed regression rather than adjacent cleanup.

The exact twelve-path Git tree fingerprint is
`cdd3a69a72a67ccaf130bfacb4a0a5bf380a32de354190c412b8130503e388a5`.
The full binary patch SHA-256 is
`85d7ffca2eb95f84f3c10ee33d8caccdb4c06f7c9c544dce359af3b8f2d57502`;
the fix-only patch SHA-256 is
`61eeb757044c6959ca2eba8840fdbf4f9f30e596d847351cee738363599796c8`.
