# Story V8 Case Fees Instruction UI Current Adoption

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-CASE-FEES-INSTRUCTION-UI-20260712-01` (ordinal `268`).
- Product commit: `1420fb8`.

The case fee tab now records `PAY`, `HOLD` and `ABANDON` instructions only against persisted
official-fee obligations. Each user attempt sends exactly the instruction and an idempotency key.
A transport failure retains that key for an explicit retry; a received success or business error
retires it, and a different instruction starts a new attempt.

Instruction results and errors remain separate from the immutable lifecycle-overlay status. Only a
successful `PAY` response can expose a user-click draft link, using the obligation identifier
returned by the server. The UI never automatically retries, navigates, creates a draft, changes a
PayList or payment, or mutates the overlay snapshot.

The focused Playwright suite passed three tests, the preceding fee-view regression suite passed
five tests, and the combined serial run passed all eight. Scoped ESLint and exact-path diff checks
passed. Typecheck retained only five unrelated baseline diagnostics. Independent High review
approved the exact closure with P0/P1/P2 all zero.
