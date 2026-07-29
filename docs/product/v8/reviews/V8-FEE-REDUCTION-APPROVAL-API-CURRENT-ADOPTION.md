# Independent Review — V8 Fee Reduction Approval API Current Adoption

## Exact reviewed range

- Base: `3c0ee20730c9ce6727639e8bdd9a1611f759853c`
- Story commit: `bd8590eed6ef2b0636ef54035501a61c75f7fbd9`
- Exact patch SHA-256:
  `074e283848308fe3a21582b8dce690a707346f5bde02e4e01abbb0ae0455131b`
- Story SHA-256:
  `36ca8b82cadd9aa051859dc5fa0f1f029e5b94e13d61515723ea1db0fbb3fb3f`

Verdict: APPROVED

- P0: 0
- P1: 0
- P2: 0

## Findings closed before acceptance

The first two candidate commits were rejected and are not the accepted delivery head.
Independent review required and then verified:

1. strict canonical fee-scope JSON, duplicate-key rejection, non-empty sorted unique
   canonical fee codes, lowercase SHA-256 shape, and exact hash matching;
2. exact evidence identity projection and post-validation rather than accepting any
   non-null identity;
3. visibility of corrupt confirmed evidence rows so they fail closed instead of being
   silently removed by the query.

The final query projects the SQLite-safe exact identity equality as `is_current`, filters
only by requested evidence case and confirmed approval status, and validates exact
case/lineage/key plus `is_current is True` before returning an item. The independent real
SQLite probe now returns
`409:FEE_REDUCTION_APPROVAL_SOURCE_IDENTITY_CORRUPT` for a malformed persisted key.

## Fresh verification

- Row 95 and row 96 focused tests: `39 passed`, with three existing deprecation warnings.
- Independent real SQLite malformed-identity probe: deterministic `409`.
- Scoped Ruff: passed.
- Format check: the four Python files were already formatted.
- Exact-range diff check: passed.
- Exact five-path story scope and clean reviewed worktree: confirmed.
- Existing row-105 preview body remained unchanged.

The implementer did not approve the story and the reviewer made no file changes.
