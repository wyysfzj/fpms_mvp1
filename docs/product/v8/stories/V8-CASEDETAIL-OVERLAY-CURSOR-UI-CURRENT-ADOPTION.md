# Story V8 Case Detail Overlay Cursor UI Current Adoption

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-CASEDETAIL-OVERLAY-CURSOR-UI-20260712-01` (ordinal `274`).
- Product commits: `0958536`, `29b3cba`.

The case-detail overlay now traverses milestone pages using the first accepted lifecycle revision
and each exact server cursor. Milestones alone accumulate, preserve ascending received order and
deduplicate by sequence with the first accepted item winning. Every accepted later page atomically
replaces all other projection fields, including the complete ordered 29-entry decision-gate
snapshot.

Revision drift, internally non-ascending pages, a missing or non-advancing cursor, and an unseen
backward milestone all fail closed before changing accepted state. The explicit retry therefore
uses the same cursor and frozen revision. Seen overlaps remain valid. The UI does not claim complete
history while more pages exist and stops offering pagination after the terminal page.

The focused Playwright suite passed two tests and the Row273 regression passed one test serially.
Scoped ESLint, typecheck-baseline comparison and exact-path diff checks passed. Independent High
review approved the corrected exact closure with P0/P1/P2 all zero.
