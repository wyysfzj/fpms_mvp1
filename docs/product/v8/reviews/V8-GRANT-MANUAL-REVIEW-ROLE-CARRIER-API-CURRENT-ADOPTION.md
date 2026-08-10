# Independent Review — Grant Manual-review Role Carrier API

- Review class: `PROTECTED`.
- Reviewed story range: `c1b1682^..543d1a8`.
- Final correction commit: `543d1a8e5c6e9a062ab15fe8b532853f9b92ae11`.
- Task SHA-256:
  `dbc0a85a562b2923ec054a6e2cf619b864634985c3087c289a4d5ddd3e5a81c7`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact three-path candidate adds only authenticated publication and revocation routes for the
five Scheme A institution duty slots. Strict schemas expose only client-owned role, version,
effective-interval, CAS and idempotency fields. Open-ended `effective_to=null` is valid; malformed
UUIDs, aware timestamps, invalid intervals, extra fields and client-owned actor/time fields are
rejected before service delegation.

Both routes require `SystemParam.Edit`, inject the authenticated user and one server time, delegate
once to the accepted fail-closed service, and return `201 CREATED` or `200 REUSED`. Path/body
revocation identity is exact. Service or commit failure rolls back; the API neither queries carrier
tables nor adds roles, users, memberships, defaults, operational evidence or legal-state behavior.

Fresh independent verification passed: focused API pytest `7 passed`, shared-router regressions
`34 passed`, role-service regressions `24 passed`, scoped Ruff passed, and exact range diff-check
passed. The exact three-path Git tree fingerprint is
`6215434c1ea6227f1e36c4511f842b1643cb4d7f1bae57e3f4d20968b389f2f2`.
