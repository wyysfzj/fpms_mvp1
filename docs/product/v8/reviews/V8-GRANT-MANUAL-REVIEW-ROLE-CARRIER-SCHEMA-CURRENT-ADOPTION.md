# Independent Review — Grant Manual-review Role Carrier Schema

- Review class: `PROTECTED`.
- Reviewed commit: `1a3f845b98514bf6be39c720f02f40f654e653c1`.
- Task SHA-256:
  `79e4610af6f7a08a07b706769de88ebd0ec740e6cc2e54eeb9f514fbcd54e19e`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact four-path candidate adds only one empty, versioned institution role-configuration
carrier for the five Scheme A duties. It reuses existing RBAC roles and users but creates no role,
user, membership, permission, default, seed or fallback. Same-role slot assignments are structurally
allowed because the customer requires different actual users at action time, not different role
IDs; that separation remains mandatory in the later resolver and controlled actions.

Migration and ORM expose exactly 21 ordered columns, seven `ON DELETE RESTRICT` foreign keys,
three uniques, five checks and one interval index. A current `REVOKED` successor can shadow older
active history, preventing implicit fallback. Only technical `created_at`/`updated_at` have server
defaults.

Fresh independent verification passed: focused schema pytest `4 passed`, scoped Ruff passed,
Alembic reported exactly `v8_grant_manual_review_role_01 (head)`, clean temporary SQLite
upgrade/current reached that head with zero configuration/RBAC rows, registry import/export and
exact diff checks passed. The exact four-path Git tree fingerprint is
`1dd9696e0609d8de56ec639e4270bdacc70ce89e8b95cebb2a9efeeb732349f6`.
