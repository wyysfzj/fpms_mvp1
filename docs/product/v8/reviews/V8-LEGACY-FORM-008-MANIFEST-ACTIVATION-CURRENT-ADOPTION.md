# Independent Review — Legacy Form 008 Manifest Activation

- Review class: `PROTECTED`.
- Reviewed commits: `578f4c2c1b00bc401b658e5a596d9264a5f46e73`,
  `1f696a68d07dcb24b0921e8a74a97fa9b285be52`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact two-path candidate orders the form-008 activation before its sole OUT-008 child. The
accepted classification is exactly `INTERNAL_ONLY`; the form remains internal/reference-only,
with no current-official exception or official-submission activation. All named prerequisites,
accepted source commits, task dependencies and allowlists are intact. The correction adds only
the previously omitted UI-clarity prerequisite assertion to the focused contract test.

The child retains serialized `official_notice_catalog.py` order 10 and `seed_dev.py` order 13
ownership; global SQLite verification remains serialized. No product, schema, catalog,
coverage-ledger, task-card, seed or adjacent form lane changed.

Fresh verification passed: focused pytest `3 passed`, scoped Ruff and exact diff checks. Combined
candidate patch SHA-256 is
`d24e85c01c3afbd257fada461deb8333a930deceda9afb4c32ec3ae5d25f69e0` and the canonical
two-path Git tree SHA-256 is
`a68f4925d4c2468807fb0422a37d55a78726b03c6af851331a9c7012ad82072a`.
