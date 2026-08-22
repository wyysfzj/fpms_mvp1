# V8 Overlay Lane Integrated Acceptance Contract

This binding resolves the frozen row `269`–`272` testability cycle without changing product
semantics or file ownership.

- Rows 269, 270 and 271 each own and commit only their new lane component and exact Playwright
  specification. Their RED is the component's absence/unmounted state. They may reach a durable
  implementation checkpoint before adoption; no row is reported PASS at that point.
- Row 272 alone owns `CaseLifecycleOverlay.vue` and `CaseDetail.vue`, loads the accepted overlay and
  mounts the three predecessor components in left/center/right order. It must not edit their source
  or tests.
- After the row-272 integration commit, run all four targeted Playwright specs serially with one
  worker, scoped ESLint for the five exact component/page files, and one frontend typecheck. The
  integrated commit is the authorized visible test seam for predecessor lanes, not part of their
  source ownership.
- Independently review each exact component commit and the integration commit. Once the integrated
  tree is GREEN, adopt rows 269, 270 and 271 in dependency order using their own source/test
  fingerprints, then adopt row 272. This does not permit cyclic product dependencies, a test-only
  route, router changes or bypassed acceptance.

New labels are Simplified Chinese. Where no frozen Chinese enum vocabulary exists, show a Chinese
field label with the exact server value; do not invent a status translation or business category.
The single integrated typecheck is baseline-subtracted from the currently captured unrelated
diagnostics and must introduce no changed-path diagnostic.
