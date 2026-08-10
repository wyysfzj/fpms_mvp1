# Independent Review — Grant-evidence Source Carrier API

- Review class: `PROTECTED`.
- Reviewed commit: `667a96d55aa2fa2b86f256e37c1483bee3ce30a3`.
- Verification-path overlay: `2cc347c05c9a27f76a0266cd35d4c45d224cf60c`.
- Task SHA-256:
  `252b73f40e21deebeeb1e44f61c94f7a4dee4c9106fc4d82e1a518529c8a3d52`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact three-path candidate adds only the six frozen authenticated source-directory and
institution source-configuration mutation endpoints. It uses `SystemParam.Edit`, injects the
authenticated actor and one server UTC-naive timestamp, delegates exactly once to the accepted
service, preserves dynamic create/reuse statuses and performs one commit or rollback.

Strict request schemas reject unknown/client-owned actor or timestamp fields, invalid values and
retire/revoke path-body mismatches before service invocation. The API neither queries carrier ORM
tables nor resolves, defaults or ingests a source, and it cannot confirm legal status.

Fresh independent verification passed: focused pytest `26 passed`, exact live decision-gate and
config-readiness regressions `32 passed`, scoped Ruff passed and the exact three-path diff check
passed. The exact three-path Git tree fingerprint is
`7e4c38191861dbb4cd828b1393e7676971b316d720a1020dbcc77dcff6e49466`.
