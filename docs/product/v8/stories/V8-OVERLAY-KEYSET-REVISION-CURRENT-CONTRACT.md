# Story V8-OVERLAY-KEYSET-REVISION-CURRENT-CONTRACT

- Risk: `PROTECTED`
- Outcome: close catalog row `264` with stable milestone-only keyset pagination at a frozen
  lifecycle revision, while returning the complete row-263 gate snapshot on every page.
- Catalog ID: `FPMS-V8-OVERLAY-KEYSET-REVISION-20260712-01`.
- Authority: the row-264 Ultra freeze; this story binds its exact contract to C3 delivery.
- Dependency: begin only after the row-263 decision-gate join is independently accepted.

## Exact closure

Keep full-history loading and validation through revision `R` for center integrity. Select the
milestone page with `case_id`, `sequence > after_sequence`, `sequence <= R`, ascending sequence
and ID, and `limit + 1`. Return only the first `limit`; the extra row sets `has_more`. Set
`next_cursor` to the last returned sequence only when `has_more`, otherwise null. Later rows above
the first page's frozen `R` never enter that traversal. An empty terminal page is valid.

The complete ordered 29-entry decision-gate snapshot remains present on every page. Each request
uses one `generated_at` for all resolver commands in the caller transaction, preserves duplicate
legacy composite identities and their requested/resolved scope provenance, and never requests
`ALL-22`.

## Predecessor-test compatibility

The accepted row-260 center test deliberately used `limit=1` before row 264 owned pagination and
therefore asserted all three milestones plus terminal cursor fields. Row 264 changes that exact
observable by design. Its implementation may update only that one predecessor test invocation to
use a limit large enough to retain the test's center/document purpose; it must not weaken any
center assertion or absorb a second behavior. This is a successor-owned test migration, not a
product compatibility rule or a change to row-260 acceptance history.

## Verification and non-goals

The focused test proves a 121-row, three-page traversal without gaps or duplicates, exclusion of
a post-freeze row, intermediate/final/empty cursors, and the complete gate snapshot on every page.
Run the focused overlay center/document/fee/decision-gate regressions, scoped Ruff/format/diff,
then independent High review.

No decision resolver, endpoint, UI, schema, fee/document behavior, alternative cursor, offset
pagination or adjacent cleanup. Rollback reverts only the row-264 service/test change, the exact
predecessor-test invocation migration and its adoption.
