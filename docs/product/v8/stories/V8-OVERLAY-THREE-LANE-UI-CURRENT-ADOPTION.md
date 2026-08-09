# Story V8 Overlay Three-Lane UI Current Adoption

- Risk: `PROTECTED`
- Catalog rows: `269`–`272`.
- Component commits: `13435c5`, `d84eb45`, `4eb32ef`, `b4abb66`.
- Integration commits: `8667862`, `b5d5fc0`.

The case-detail page now displays the document evidence lane on the left, the wider case lifecycle
lane in the center and the fee obligation lane on the right. It replaces the page's legacy stepper
display without deleting the reusable legacy component. One accepted lifecycle-overlay request
supplies all three lanes and the fee tab consumer, preventing distinct visible snapshots.

The center lane renders current business stage, official procedure stage and legal status plus only
confirmed center changes. The document lane renders version, derivation, work-package, submission,
receipt and task facts. The fee lane renders GOV/SERVICE obligations, all seven independent statuses,
lines, related facts and supersession provenance. New labels are Simplified Chinese; server values,
dates and decimal strings remain unmodified.

The integrated single-worker Playwright tranche passed all nine Row267/269–272 tests. Scoped ESLint
passed on all six affected Vue files. Typecheck retained only five unrelated baseline diagnostics.
Independent High review approved each component checkpoint and the corrected integration with
P0/P1/P2 all zero.
